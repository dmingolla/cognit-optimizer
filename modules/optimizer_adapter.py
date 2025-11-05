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

        # Use estimated_load for load, but capacity_load = 1.0 for optimizer
        load = assignment['estimated_load']
        capacity_load = 1.0  # Fixed capacity load for optimizer

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

def run_dry_run_optimization():
    """Run a dry-run optimization with real data from database and OpenNebula.

    Returns:
        Tuple of (allocations_dict, n_vms_dict, objective_value) or None if failed
    """
    try:
        # Import required modules
        from modules.db_adapter import get_device_assignments
        from modules.opennebula_adapter import get_cluster_pool

        print("Running dry-run optimization with real data...")

        # Get real device assignments from database
        assignments = get_device_assignments()
        if not assignments:
            print("No device assignments found in database")
            return None

        print(f"Found {len(assignments)} device assignments")

        # Get real cluster pool from OpenNebula
        clusters = get_cluster_pool()
        if not clusters:
            print("No clusters found in OpenNebula")
            return None

        print(f"Found {len(clusters)} clusters")

        # Get cluster IDs for baseline mapping (all clusters feasible)
        cluster_ids = [cluster.id for cluster in clusters]

        # Create devices from assignments using baseline mapping
        devices = create_devices_from_assignments(assignments, cluster_ids)

        print(f"Created {len(devices)} Device objects for optimization")

        # Print sample device info
        if devices:
            sample_device = devices[0]
            print(f"Sample device {sample_device.id}: load={sample_device.load:.4f}, capacity_load={sample_device.capacity_load}, feasible_clusters={len(sample_device.cluster_ids)}")

        # Print sample cluster info
        if clusters:
            sample_cluster = clusters[0]
            print(f"Sample cluster {sample_cluster.id}: max_capacity={sample_cluster.max_capacity}, carbon_intensity={sample_cluster.carbon_intensity}")

        # Run optimization
        print("Running optimization...")
        result = optimize_device_assignments(devices, clusters)

        if result:
            allocs, n_vms, objective = result
            print("Optimization successful!")
            if objective is not None:
                print(f"Objective value: {objective:.2f}")
            else:
                print("Objective value: None")
            print(f"Device allocations: {allocs}")
            print(f"VM counts per cluster: {n_vms}")
            return result
        else:
            print("Optimization failed")
            return None

    except Exception as e:
        print(f"Dry-run optimization error: {e}")
        import traceback
        traceback.print_exc()
        return None
