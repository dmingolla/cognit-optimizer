#!/usr/bin/env python3
"""Database adapter for reading device assignments."""

import sys
import os

# Add paths for imports
sys.path.insert(0, '/home/ubuntu/cognit-frontend/src')  # Add cognit-frontend src for db_manager
sys.path.insert(0, os.path.dirname(__file__))  # Add current directory for device_alloc

# Mock minimal config to avoid pyoneai dependency
class MockConf:
    DB_PATH = '/home/ubuntu/cognit-frontend/database/device_cluster_assignment.db'
    DB_CLEANUP_DAYS = 30

# Replace the import
sys.modules['cognit_conf'] = MockConf

def verify_db_connectivity() -> bool:
    """Verify database connectivity and print device information."""
    try:
        import db_manager

        # Initialize DB manager
        db = db_manager.DBManager()

        # Get device count
        device_count = db.get_distinct_device_count()

        # Get all device IDs
        device_ids = db.get_all_device_ids()

        print(f"Found {device_count} devices: {device_ids}")

        # Get assignment details for first device if any exist
        if device_ids:
            first_device = device_ids[0]
            assignment = db.get_device_assignment(first_device)
            if assignment:
                print(f"Sample assignment for device {first_device}:")
                print(f"  Cluster ID: {assignment['cluster_id']}")
                print(f"  Flavour: {assignment['flavour']}")
                print(f"  Estimated Load: {assignment['estimated_load']}")
                print(f"  App Req JSON keys: {list(assignment['app_req_json'].keys()) if assignment['app_req_json'] else 'None'}")

        return True

    except Exception as e:
        print(f"Database connectivity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_device_assignments():
    """Get all device assignments from database."""
    try:
        import db_manager
        db = db_manager.DBManager()
        device_ids = db.get_all_device_ids()

        assignments = []
        for device_id in device_ids:
            assignment = db.get_device_assignment(device_id)
            if assignment:
                assignments.append(assignment)

        return assignments

    except Exception as e:
        print(f"Failed to get device assignments: {e}")
        return []
