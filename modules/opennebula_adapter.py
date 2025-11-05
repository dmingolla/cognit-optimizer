#!/usr/bin/env python3
"""OpenNebula adapter for cluster pool management."""

import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.dirname(__file__))  # Add current directory for device_alloc

def verify_opennebula_connectivity() -> bool:
    """Verify OpenNebula connectivity and print cluster information."""
    try:
        from device_alloc.model import create_cluster_pool
        from device_alloc.xmlrpc_client import OnedServerProxy

        print("Testing OpenNebula connectivity...")

        # Try to create cluster pool
        with OnedServerProxy() as oned_client:
            clusters = create_cluster_pool(oned_client)

            print(f"Found {len(clusters)} clusters")

            # Print sample cluster info
            if clusters:
                sample_cluster = clusters[0]
                print(f"Sample cluster {sample_cluster.id}:")
                print(f"  Capacity: {sample_cluster.capacity}")
                print(f"  Max Capacity: {sample_cluster.max_capacity}")
                print(f"  Carbon Intensity: {sample_cluster.carbon_intensity}")
                print(f"  Energy breakpoints: {len(sample_cluster.energy)} points")

            return True

    except Exception as e:
        print(f"OpenNebula connectivity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_cluster_pool():
    """Get cluster pool from OpenNebula."""
    try:
        from device_alloc.model import create_cluster_pool
        from device_alloc.xmlrpc_client import OnedServerProxy

        with OnedServerProxy() as oned_client:
            return create_cluster_pool(oned_client)

    except Exception as e:
        print(f"Failed to get cluster pool: {e}")
        return []
