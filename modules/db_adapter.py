import sys
import os

sys.path.insert(0, '/home/ubuntu/cognit-frontend/src')

class MockConf:
    DB_PATH = '/home/ubuntu/cognit-frontend/database/device_cluster_assignment.db'
    DB_CLEANUP_DAYS = 30

sys.modules['cognit_conf'] = MockConf

def get_device_assignments():
    """Phase 1: Get device assignments from DB."""
    import db_manager
    db = db_manager.DBManager()
    device_ids = db.get_all_device_ids()

    assignments = []
    for device_id in device_ids:
        assignment = db.get_device_assignment(device_id)
        if assignment:
            assignments.append(assignment)

    return assignments
