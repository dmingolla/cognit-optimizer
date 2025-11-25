import os

# Database configuration
DB_PATH = '/root/devices_local_database/device_cluster_assignment.db'
DB_CLEANUP_DAYS = 30

# Cognit frontend paths - try installed location first, then dev location
COGNIT_FRONTEND_SRC = (
    '/usr/lib/one/cognit-frontend' 
    if os.path.exists('/usr/lib/one/cognit-frontend') 
    else '/root/cognit-frontend/src'
)

# OpenNebula configuration
ONE_XMLRPC_ENDPOINT = os.getenv('ONE_XMLRPC_ENDPOINT')
ONE_AUTH_USER = os.getenv('ONE_AUTH_USER')
ONE_AUTH_PASSWORD = os.getenv('ONE_AUTH_PASSWORD')

# OpenNebula API response keys
CLUSTER_POOL_KEY = 'CLUSTER_POOL'
CLUSTER_KEY = 'CLUSTER'
TEMPLATE_KEY = 'TEMPLATE'
DOCUMENT_KEY = 'DOCUMENT'
ID_KEY = 'ID'

# Optimizer configuration
OPTIMIZER_ENABLED = True
OPTIMIZER_UPDATE_INTERVAL_SECONDS = 300
