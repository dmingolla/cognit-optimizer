import sys

# Mock pyoneai before importing cognit_conf to avoid dependency
class MockFloat:
    pass

class MockMetricType:
    GAUGE = 'gauge'

class MockMetricAttributes:
    def __init__(self, name, type, dtype):
        self.name = name
        self.type = type
        self.dtype = dtype

class MockPyoneai:
    Float = MockFloat
    MetricType = MockMetricType
    MetricAttributes = MockMetricAttributes

sys.modules['pyoneai'] = MockPyoneai
sys.modules['pyoneai.core'] = MockPyoneai

sys.path.insert(0, '/home/ubuntu/cognit-frontend/src')

def get_device_assignments():
    """Retrieve all device assignments from database."""
    import db_manager
    db = db_manager.DBManager()
    device_ids = db.get_all_device_ids()

    assignments = []
    for device_id in device_ids:
        assignment = db.get_device_assignment(device_id)
        if assignment:
            assignments.append(assignment)

    return assignments

def update_device_cluster_assignments(allocations):
    """Update device cluster assignments in database only when changed."""
    import db_manager
    db = db_manager.DBManager()
    updated_count = 0
    for device_id, new_cluster_id in allocations.items():
        current = db.get_device_assignment(device_id)
        if current and current['cluster_id'] != new_cluster_id:
            db.update_device_assignment(
                device_id=device_id,
                cluster_id=new_cluster_id,
                flavour=current['flavour'],
                app_req_id=current['app_req_id'],
                app_req_json=current['app_req_json']
            )
            updated_count += 1

    return updated_count
