import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

def get_cluster_pool() -> list:
    """Retrieve cluster pool from OpenNebula."""
    from device_alloc import create_cluster_pool, OnedServerProxy

    with OnedServerProxy() as oned_client:
        return create_cluster_pool(oned_client)

def get_app_requirement(app_req_id: int) -> dict:
    """Retrieve app requirement from OpenNebula by ID using OnedServerProxy."""
    from device_alloc import OnedServerProxy

    try:
        with OnedServerProxy() as client:
            # Get document info
            result = client('one.document.info', app_req_id)
            if result and 'DOCUMENT' in result:
                # Parse the template which contains the app requirements
                template = result['DOCUMENT'].get('TEMPLATE', {})
                return template
    except Exception:
        return {}

def get_feasible_clusters_for_device(app_req_id: int) -> list[int]:
    """Get feasible cluster IDs for a device based on its app requirements using clusters_ids_get."""
    # Get fresh app requirements from OpenNebula
    app_req = get_app_requirement(app_req_id)
    if not app_req:
        return []

    # Extract filtering parameters
    geolocation = app_req.get('GEOLOCATION')
    flavour = app_req.get('FLAVOUR')
    is_confidential = app_req.get('IS_CONFIDENTIAL')
    providers = app_req.get('PROVIDERS')
    
    # Use clusters_ids_get from cognit-frontend
    from modules.config import COGNIT_FRONTEND_SRC, ONE_XMLRPC_ENDPOINT
    
    # Clean up sys.path to avoid conflicts with /usr/lib/one/python
    # TODO: Temporary fix to avoid conflicts with /usr/lib/one/python
    original_path = sys.path.copy()
    sys.path = [p for p in sys.path if '/usr/lib/one/python' not in p]
    sys.path.insert(0, COGNIT_FRONTEND_SRC)
    
    try:
        import opennebula as on
        import pyone

        # Create pyone client using OnedServerProxy credentials
        from device_alloc import OnedServerProxy
        with OnedServerProxy() as proxy:
            # Get session from OnedServerProxy
            one = pyone.OneServer(ONE_XMLRPC_ENDPOINT, session=proxy._session)
            
            feasible_cluster_ids = on.clusters_ids_get(
                one=one,
                geolocation=geolocation,
                flavour=flavour,
                is_confidential=is_confidential,
                providers=providers
            )

        return feasible_cluster_ids
    finally:
        sys.path = original_path
