#!/usr/bin/env python3
"""Optimizer adapter for device-cluster assignment optimization."""

import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.dirname(__file__))  # Add current directory for device_alloc

def verify_optimizer() -> bool:
    """Verify optimizer works with a toy example."""
    try:
        from device_alloc.model import Cluster, Device
        from device_alloc.optimizer import DeviceOptimizer

        # Toy clusters
        clusters = [
            Cluster(
                id=1,
                capacity=2.0,
                max_capacity=2.0,
                carbon_intensity=500.0,
                energy=[(0.0, 5.0), (2.0, 10.0)]
            ),
            Cluster(
                id=2,
                capacity=4.0,
                max_capacity=4.0,
                carbon_intensity=1000.0,
                energy=[(0.0, 6.0), (2.0, 12.0), (4.0, 16.0)]
            )
        ]

        # Toy devices
        devices = [
            Device(id=11, load=0.1, capacity_load=0.1, cluster_ids=[1, 2]),
            Device(id=12, load=0.2, capacity_load=0.2, cluster_ids=[1, 2])
        ]

        # Run optimizer
        opt = DeviceOptimizer(devices=devices, clusters=clusters, msg=False)
        result = opt.optimize()

        if result:
            allocs, n_vms, objective = result
            print(f"Allocations: {allocs}")
            print(f"N_VMs: {n_vms}")
            print(f"Objective: {objective:.2f}")
            return True
        else:
            print("Optimizer returned empty result")
            return False

    except Exception as e:
        print(f"Optimizer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_devices_from_assignments(assignments, cluster_ids=None):
    """Create Device objects from database assignments.

    Args:
        assignments: List of device assignment dictionaries from DB
        cluster_ids: List of available cluster IDs (if None, uses all available)

    Returns:
        List of Device objects
    """
    from device_alloc.model import Device

    devices = []

    for assignment in assignments:
        device_id = assignment['device_id']

        # Use estimated_load for both load and capacity_load initially
        load = assignment['estimated_load']
        capacity_load = load

        # For now, allow all clusters or use provided list
        if cluster_ids is None:
            # This will be updated when we implement per-device feasible clusters
            # For now, assume all clusters are feasible
            feasible_cluster_ids = []  # Will be filled based on cluster pool
        else:
            feasible_cluster_ids = cluster_ids

        device = Device(
            id=device_id,
            load=load,
            capacity_load=capacity_load,
            cluster_ids=feasible_cluster_ids
        )
        devices.append(device)

    return devices

def optimize_device_assignments(devices, clusters):
    """Run optimization on devices and clusters.

    Args:
        devices: List of Device objects
        clusters: List of Cluster objects

    Returns:
        Tuple of (allocations_dict, n_vms_dict, objective_value) or None if failed
    """
    try:
        from device_alloc.optimizer import DeviceOptimizer

        opt = DeviceOptimizer(devices=devices, clusters=clusters, msg=False)
        result = opt.optimize()

        if result:
            allocs, n_vms, objective = result
            return allocs, n_vms, objective
        else:
            print("Optimization failed - no solution found")
            return None

    except Exception as e:
        print(f"Optimization error: {e}")
        import traceback
        traceback.print_exc()
        return None
