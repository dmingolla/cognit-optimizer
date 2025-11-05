import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

def create_devices_from_assignments(assignments, cluster_ids=None):
    """Create Device objects from database assignments."""
    from device_alloc.model import Device

    devices = []
    for assignment in assignments:
        device_id = assignment['device_id']
        load = assignment['estimated_load']
        capacity_load = 1.0

        feasible_cluster_ids = cluster_ids if cluster_ids is not None else []

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

    # Get current assignments before optimization
    assignments_before = get_device_assignments()
    print(f"Input devices before optimization:")
    for assignment in assignments_before:
        print(f"  {assignment['device_id']}: cluster {assignment['cluster_id']}, load {assignment['estimated_load']}")

    assignments = assignments_before
    clusters = get_cluster_pool()
    cluster_ids = [cluster.id for cluster in clusters]

    devices = create_devices_from_assignments(assignments, cluster_ids)
    result = optimize_device_assignments(devices, clusters)

    print(f"Input: {len(devices)} devices, {len(clusters)} clusters")
    if result:
        allocs, n_vms, objective = result
        print(f"VM distribution per cluster: {n_vms}")

        # Update database with new allocations
        updated_count = update_device_cluster_assignments(allocs)
        print(f"Database updates: {updated_count} devices changed cluster assignment")

        # Verify the updates
        assignments_after = get_device_assignments()
        print(f"Input devices after optimization:")
        for assignment in assignments_after:
            old_cluster = next((a['cluster_id'] for a in assignments_before if a['device_id'] == assignment['device_id']), None)
            change_indicator = " (CHANGED)" if old_cluster != assignment['cluster_id'] else ""
            print(f"  {assignment['device_id']}: cluster {assignment['cluster_id']}{change_indicator}, load {assignment['estimated_load']}")

    return result
