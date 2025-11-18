"""Module for scaling clusters based on optimizer output."""

import requests
from urllib3.exceptions import InsecureRequestWarning
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.logger import get_logger
from modules.config import ONE_XMLRPC_ENDPOINT, ONE_AUTH_USER, ONE_AUTH_PASSWORD
from modules.db_adapter import update_device_cluster_assignments

# Suppress SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = get_logger(__name__)


def get_cluster_template(cluster_id: int) -> Optional[dict]:
    """Get cluster template from OpenNebula."""
    if not ONE_XMLRPC_ENDPOINT or not ONE_AUTH_USER or not ONE_AUTH_PASSWORD:
        logger.error("OpenNebula credentials not configured")
        return None
    
    try:
        import pyone
        session = f"{ONE_AUTH_USER}:{ONE_AUTH_PASSWORD}"
        one = pyone.OneServer(ONE_XMLRPC_ENDPOINT, session=session)
        cluster = one.cluster.info(cluster_id)
        return dict(cluster.TEMPLATE)
    except Exception as e:
        logger.error(f"Failed to get cluster template for cluster {cluster_id}: {e}")
        return None


def get_flavour_from_template(cluster_template: dict) -> Optional[str]:
    """Get first flavour from cluster template FLAVOURS key."""
    flavours_str = cluster_template.get('FLAVOURS', '')
    if not flavours_str:
        return None
    # Get first flavour without creating a list
    comma_idx = flavours_str.find(',')
    first_flavour = flavours_str[:comma_idx] if comma_idx != -1 else flavours_str
    return first_flavour.strip() or None


def construct_endpoint(cluster_template: dict, flavour: str, target_cardinality: int) -> Optional[str]:
    """Construct the scaling endpoint URL.
    
    Format: {EDGE_CLUSTER_FRONTEND}/{flavour}/v1/scale?target_cardinality={target_cardinality}
    """
    edge_cluster_frontend = cluster_template.get('EDGE_CLUSTER_FRONTEND')
    if not edge_cluster_frontend:
        return None
    
    base_url = edge_cluster_frontend.rstrip('/')
    return f"{base_url}/{flavour}/v1/scale?target_cardinality={target_cardinality}"


def call_scale_endpoint(endpoint: str) -> bool:
    """Call the scaling endpoint with POST request."""
    try:
        response = requests.post(endpoint, verify=False)
        success = response.status_code in [200, 201, 202]
        if success:
            logger.info(f"Successfully scaled cluster via {endpoint} (status: {response.status_code})")
        else:
            logger.warning(f"Failed to scale cluster via {endpoint} (status: {response.status_code}, response: {response.text[:200]})")
        return success
    except Exception as e:
        logger.error(f"Error calling scale endpoint {endpoint}: {e}")
        return False


def scale_cluster(cluster_id: int, target_cardinality: int) -> bool:
    """Scale a single cluster to target cardinality.
    
    Args:
        cluster_id: The cluster ID to scale
        target_cardinality: Target number of VMs for the cluster
        
    Returns:
        True if scaling was successful, False otherwise
    """
    
    cluster_template = get_cluster_template(cluster_id)
    if not cluster_template:
        return False
    
    flavour = get_flavour_from_template(cluster_template)
    if not flavour:
        logger.warning(f"Could not determine flavour for cluster {cluster_id}")
        return False
    
    endpoint = construct_endpoint(cluster_template, flavour, target_cardinality)
    if not endpoint:
        logger.warning(f"Could not construct endpoint for cluster {cluster_id} (EDGE_CLUSTER_FRONTEND missing)")
        return False
    
    return call_scale_endpoint(endpoint)


def scale_clusters_and_update_db(n_vms: dict[int, int], allocs: dict) -> int:
    """
    Scale clusters in parallel and update DB for each successfully scaled cluster.
    
    Args:
        n_vms: Cluster ID to target cardinality mapping
        allocs: Device ID to cluster ID mapping
        
    Returns:
        Total number of devices updated in database
    """
    n_clusters_to_scale = len(n_vms)
    logger.info("=== CLUSTER SCALING ===")
    
    if n_clusters_to_scale == 0:
        logger.info("No clusters to scale")
        return 0
    
    logger.info(f"Scaling {n_clusters_to_scale} clusters in parallel")
    
    total_updated = 0
    max_workers = max(1, n_clusters_to_scale)  # Ensure at least 1 worker
    
    def scale_with_id(cid: int, card: int) -> tuple[int, bool]:
        """Scale a single cluster and return the cluster ID and scaling result."""
        return cid, scale_cluster(cid, card)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(scale_with_id, cid, card): cid
            for cid, card in n_vms.items()
        }
        for future in as_completed(future_map):
            cid, ok = future.result()
            if ok:
                # Check which devices are assigned to the scaled cluster and update their corresponding cluster ID in the local database
                cluster_allocs = {dev_id: cluster_id for dev_id, cluster_id in allocs.items() if cluster_id == cid}
                updated = update_device_cluster_assignments(cluster_allocs)
                total_updated += updated
                if updated > 0:
                    logger.info(f"Cluster {cid} scaled successfully: {updated} devices updated")
    
    logger.info(f"Cluster scaling completed: {total_updated} total devices updated")
    return total_updated

