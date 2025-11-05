#!/usr/bin/env python3
"""Main entrypoint for the Cognit Optimizer Daemon."""

import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_optimization_cycle():
    """Run single optimization cycle with database updates."""
    from modules.optimizer_adapter import run_optimization_with_db_updates
    result = run_optimization_with_db_updates()
    return result is not None

def main():
    """Main entry point for optimizer."""
    if run_optimization_cycle():
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
