import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from modules.logger import get_logger
logger = get_logger(__name__)

def create_devices_from_assignments(assignments: list[dict]) -> list:
    """Create Device objects for the optimization algorithm from database assignments with per-device feasible clusters."""
    from device_alloc import Device
    from modules.opennebula_adapter import get_feasible_clusters_for_device

    devices = []
    for assignment in assignments:
        device_id = assignment['device_id']
        load = assignment['estimated_load']
        capacity_load = 1.0 # TODO: Check with colleagues
        app_req_id = assignment['app_req_id']

        # Get feasible clusters for this device based on app requirements
        feasible_cluster_ids = get_feasible_clusters_for_device(app_req_id)

        device = Device(
            id=device_id,
            load=load,
            capacity_load=capacity_load,
            cluster_ids=feasible_cluster_ids
        )
        devices.append(device)

    return devices

def optimize_device_assignments(devices: list, clusters: list) -> tuple:
    """Run optimization algorithm on devices and clusters."""
    from device_alloc import DeviceOptimizer

    opt = DeviceOptimizer(devices=devices, clusters=clusters, msg=False)
    result = opt.optimize()
    
    if result:
        allocs, n_vms, objective = result
        return allocs, n_vms, objective
    return ()

def run_optimization_with_db_updates() -> tuple | None:
    """Run complete optimization cycle with database updates."""
    from modules.db_adapter import get_device_assignments, update_device_cluster_assignments
    from modules.opennebula_adapter import get_cluster_pool, get_app_requirement
    from device_alloc import OnedServerProxy

    assignments = get_device_assignments()
    
    logger.info("=== DEVICE REQUIREMENTS ===")
    for assignment in assignments:
        device_id = assignment['device_id']
        app_req_id = assignment['app_req_id']
        app_req = get_app_requirement(app_req_id)
        if not app_req:
            logger.warning(f"{device_id}: Could not fetch app requirements (app_req_id={app_req_id})")
            continue
        logger.info(f"{device_id}: FLAVOUR={app_req.get('FLAVOUR')}, IS_CONFIDENTIAL={app_req.get('IS_CONFIDENTIAL')}, "
                    f"PROVIDERS={app_req.get('PROVIDERS')}, GEOLOCATION={app_req.get('GEOLOCATION')}")
    
    devices = create_devices_from_assignments(assignments)

    # Filter cluster pool to only include clusters that are feasible for at least one device
    all_feasible_cluster_ids = set()
    for device in devices:
        all_feasible_cluster_ids.update(device.cluster_ids)

    clusters = get_cluster_pool()
    filtered_clusters = [c for c in clusters if c.id in all_feasible_cluster_ids]

    logger.info("=== CLUSTER OPTIMIZER ATTRIBUTES ===")
    for cluster in filtered_clusters:
        logger.info(str(cluster))

    logger.info("=== CLUSTER OPENNEBULA ATTRIBUTES ===")
    with OnedServerProxy() as client:
        cluster_info = client('one.clusterpool.info')
        if 'CLUSTER_POOL' not in cluster_info or 'CLUSTER' not in cluster_info['CLUSTER_POOL']:
            logger.warning("Could not fetch cluster information")
        else:
            for cluster in clusters:
                for c in cluster_info['CLUSTER_POOL']['CLUSTER']:
                    if int(c['ID']) != cluster.id:
                        continue
                    template = c.get('TEMPLATE', {})
                    logger.info(f"Cluster {cluster.id}: FLAVOURS={template.get('FLAVOURS')}, "
                               f"IS_CONFIDENTIAL={template.get('IS_CONFIDENTIAL')}, "
                               f"PROVIDERS={template.get('PROVIDERS')}, "
                               f"GEOLOCATION={template.get('GEOLOCATION')}, "
                               f"CARBON_INTENSITY={template.get('CARBON_INTENSITY')}")
                    break

    # Run optimization on filtered clusters
    result = optimize_device_assignments(devices, filtered_clusters)

    if result:
        allocs, n_vms, objective = result
        logger.info("=== OPTIMIZATION RESULT ===")
        for device_id, cluster_id in allocs.items():
            logger.info(f"{device_id} -> Cluster {cluster_id}")
        
        updated_count = update_device_cluster_assignments(allocs)
        logger.info(f"Database updates: {updated_count} devices changed assignment")

    return result
