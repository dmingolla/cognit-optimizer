#!/usr/bin/env python3
"""Main entrypoint for the Cognit Optimizer Daemon."""

import sys
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function for the optimizer daemon."""
    logger.info("Starting Cognit Optimizer Daemon")

    try:
        # Import our modules
        from db_adapter import verify_db_connectivity
        from opennebula_adapter import verify_opennebula_connectivity
        from optimizer_adapter import verify_optimizer

        # Phase 1: Environment verification
        logger.info("=== Phase 1: Environment Verification ===")

        # 1. Verify optimizer
        logger.info("1. Verifying optimizer...")
        if not verify_optimizer():
            logger.error("Optimizer verification failed")
            return 1
        logger.info("✓ Optimizer OK")

        # 2. Verify DB connectivity
        logger.info("2. Verifying database connectivity...")
        if not verify_db_connectivity():
            logger.error("Database connectivity verification failed")
            return 1
        logger.info("✓ Database OK")

        # 3. Verify OpenNebula connectivity
        logger.info("3. Verifying OpenNebula connectivity...")
        if not verify_opennebula_connectivity():
            logger.error("OpenNebula connectivity verification failed")
            return 1
        logger.info("✓ OpenNebula OK")

        logger.info("=== All Phase 1 checks passed! ===")
        return 0

    except Exception as e:
        logger.error(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
