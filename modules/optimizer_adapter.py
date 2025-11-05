import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

def create_devices_from_assignments(assignments, cluster_ids=None):
    """Phase 2: Create Device objects from DB assignments."""
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
    """Phase 2: Run optimization on devices and clusters."""
    from device_alloc.optimizer import DeviceOptimizer

    opt = DeviceOptimizer(devices=devices, clusters=clusters, msg=False)
    result = opt.optimize()

    if result:
        allocs, n_vms, objective = result
        return allocs, n_vms, objective
    return None

def run_dry_run_optimization():
    """Phase 2: Run optimization with real data."""
    from modules.db_adapter import get_device_assignments
    from modules.opennebula_adapter import get_cluster_pool

    assignments = get_device_assignments()
    clusters = get_cluster_pool()
    cluster_ids = [cluster.id for cluster in clusters]

    devices = create_devices_from_assignments(assignments, cluster_ids)
    result = optimize_device_assignments(devices, clusters)

    print(f"Input: {len(devices)} devices, {len(clusters)} clusters")
    if result:
        allocs, n_vms, objective = result
        print(f"Output: {allocs}")
        print(f"VMs: {n_vms}")

    return result
