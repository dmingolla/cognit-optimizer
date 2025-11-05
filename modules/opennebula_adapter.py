import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

def get_cluster_pool():
    """Phase 1: Get cluster pool from OpenNebula."""
    from device_alloc.model import create_cluster_pool
    from device_alloc.xmlrpc_client import OnedServerProxy

    with OnedServerProxy() as oned_client:
        return create_cluster_pool(oned_client)
