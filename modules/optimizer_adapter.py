import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

def create_devices_from_assignments(assignments):
    """Create Device objects from database assignments with per-device feasible clusters."""
    from device_alloc.model import Device
    from modules.opennebula_adapter import get_feasible_clusters_for_device

    devices = []
    for assignment in assignments:
        device_id = assignment['device_id']
        load = assignment['estimated_load']
        capacity_load = 1.0
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

def optimize_device_assignments(devices, clusters):
    """Run optimization algorithm on devices and clusters."""
    from device_alloc.optimizer import DeviceOptimizer

    opt = DeviceOptimizer(devices=devices, clusters=clusters, msg=False)
    result = opt.optimize()
    
    if result:
        allocs, n_vms, objective = result
        return allocs, n_vms, objective
    return None

def run_optimization_with_db_updates():
    """Run complete optimization cycle with database updates."""
    from modules.db_adapter import get_device_assignments, update_device_cluster_assignments
    from modules.opennebula_adapter import get_cluster_pool

    # Get current assignments and create devices with per-device feasible clusters
    assignments = get_device_assignments()
    devices = create_devices_from_assignments(assignments)

    # Filter cluster pool to only include clusters that are feasible for at least one device
    all_feasible_cluster_ids = set()
    for device in devices:
        all_feasible_cluster_ids.update(device.cluster_ids)

    clusters = get_cluster_pool()
    filtered_clusters = [c for c in clusters if c.id in all_feasible_cluster_ids]

    # Run optimization on filtered clusters
    result = optimize_device_assignments(devices, filtered_clusters)

    # Update database with new allocations if optimization succeeded
    if result:
        allocs, n_vms, objective = result
        updated_count = update_device_cluster_assignments(allocs)
        print(f"Optimization completed: {updated_count} devices updated")

    return result
