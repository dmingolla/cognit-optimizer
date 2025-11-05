import sys

# Mock pyoneai before importing cognit_conf (required by db_manager)
class MockFloat:
    pass

class MockMetricType:
    GAUGE = 'gauge'

class MockMetricAttributes:
    def __init__(self, name, type, dtype):
        pass

class MockPyoneai:
    Float = MockFloat
    MetricType = MockMetricType
    MetricAttributes = MockMetricAttributes

sys.modules['pyoneai'] = MockPyoneai
sys.modules['pyoneai.core'] = MockPyoneai

sys.path.insert(0, '/home/ubuntu/cognit-frontend/src')

# Import and initialize DBManager once (singleton pattern ensures single instance)
import db_manager
_db = db_manager.DBManager(
    DB_PATH='/home/ubuntu/cognit-frontend/database/device_cluster_assignment.db',
    DB_CLEANUP_DAYS=30
)

def get_device_assignments():
    """Retrieve all device assignments from database."""
    device_ids = _db.get_all_device_ids()

    assignments = []
    for device_id in device_ids:
        assignment = _db.get_device_assignment(device_id)
        if assignment:
            assignments.append(assignment)

    return assignments

def update_device_cluster_assignments(allocations):
    """Update device cluster assignments in database only when changed."""
    updated_count = 0
    for device_id, new_cluster_id in allocations.items():
        current = _db.get_device_assignment(device_id)
        if current and current['cluster_id'] != new_cluster_id:
            _db.update_device_assignment(
                device_id=device_id,
                cluster_id=new_cluster_id,
                flavour=current['flavour'],
                app_req_id=current['app_req_id'],
                app_req_json=current['app_req_json']
            )
            updated_count += 1

    return updated_count
