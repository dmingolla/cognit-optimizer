#!/usr/bin/env python3
"""Test script for optimizer environment verification."""

import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.dirname(__file__))  # Add current directory for device_alloc

def test_optimizer_toy_example():
    """Test optimizer with a toy example."""
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
            print("✓ Optimizer toy example successful!")
            print(f"  Allocations: {allocs}")
            print(f"  N_VMs: {n_vms}")
            print(f"  Objective: {objective:.2f}")
            return True
        else:
            print("✗ Optimizer returned empty result")
            return False

    except Exception as e:
        print(f"✗ Optimizer test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_optimizer_toy_example()
    sys.exit(0 if success else 1)
