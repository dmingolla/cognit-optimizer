from typing import Any
from modules.logger import get_logger

logger = get_logger(__name__)


def _format_device_requirements(device_id: str, app_req: dict[str, Any]) -> str:
    """Format device requirements for logging."""
    return (f"{device_id}: FLAVOUR={app_req.get('FLAVOUR')}, "
            f"IS_CONFIDENTIAL={app_req.get('IS_CONFIDENTIAL')}, "
            f"PROVIDERS={app_req.get('PROVIDERS')}, "
            f"GEOLOCATION={app_req.get('GEOLOCATION')}")


def _format_cluster_attributes(cluster_id: int, template: dict[str, Any]) -> str:
    """Format cluster attributes for logging."""
    return (f"Cluster {cluster_id}: FLAVOURS={template.get('FLAVOURS')}, "
            f"IS_CONFIDENTIAL={template.get('IS_CONFIDENTIAL')}, "
            f"PROVIDERS={template.get('PROVIDERS')}, "
            f"GEOLOCATION={template.get('GEOLOCATION')}, "
            f"CARBON_INTENSITY={template.get('CARBON_INTENSITY')}")

def _get_cluster_info_lookup(client: Any) -> dict[int, dict[str, Any]]:
    """Build a lookup dict mapping cluster ID to template."""
    cluster_info = client('one.clusterpool.info')
    lookup = {}
    
    if 'CLUSTER_POOL' in cluster_info and 'CLUSTER' in cluster_info['CLUSTER_POOL']:
        clusters = cluster_info['CLUSTER_POOL']['CLUSTER']
        clusters_list = clusters if isinstance(clusters, list) else [clusters]
        for c in clusters_list:
            cluster_id = int(c['ID'])
            lookup[cluster_id] = c.get('TEMPLATE', {})
    
    return lookup

def create_devices_from_assignments(assignments: list[dict]) -> list:
    """Create Device objects for the optimization algorithm from database assignments with per-device feasible clusters."""
    from device_alloc import Device
    from modules.opennebula_adapter import get_feasible_clusters_for_device

    devices = []
    for assignment in assignments:
        device_id = assignment['device_id']
        load = assignment['estimated_load']
        capacity_load = 1.0  # TODO: Check with colleagues
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
        logger.info(_format_device_requirements(device_id, app_req))
    
    devices = create_devices_from_assignments(assignments)

    # Filter cluster pool to only include clusters that are feasible for at least one device
    all_feasible_cluster_ids = {cid for device in devices for cid in device.cluster_ids}

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
            cluster_lookup = _get_cluster_info_lookup(client)
            for cluster in clusters:
                if cluster.id in cluster_lookup:
                    logger.info(_format_cluster_attributes(cluster.id, cluster_lookup[cluster.id]))
                else:
                    logger.warning(f"Cluster {cluster.id} not found in OpenNebula cluster pool")

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
