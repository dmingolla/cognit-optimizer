#!/usr/bin/env python3
"""Configuration management for the optimizer daemon."""

import os

# Database configuration
DB_PATH = '/home/ubuntu/cognit-frontend/database/device_cluster_assignment.db'
DB_CLEANUP_DAYS = 30

# Optimizer configuration
OPTIMIZER_ENABLED = True
OPTIMIZER_UPDATE_INTERVAL_SECONDS = 60  # Default interval

# Logging
LOG_LEVEL = 'INFO'

def load_config():
    """Load configuration from environment variables or config file."""
    # Could be extended to read from YAML file like cognit_conf.py
    pass
