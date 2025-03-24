#!/usr/bin/env python3
"""
Compatibility module for e-paper display
This ensures that both the old direct import method and the new package method work.
"""

import os
import sys
import logging

# Add the current directory to sys.path to enable direct imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))  # Get to project root
sys.path.insert(0, parent_dir)  # Add project root to path
sys.path.insert(0, os.path.join(parent_dir, 'utils'))  # Add utils directory to path

# Configure logging
logger = logging.getLogger(__name__)

def ensure_compatibility():
    """
    Ensure that both import methods work by setting up the proper paths
    and creating any necessary symbolic links.
    """
    try:
        # First, try importing using the package structure
        from litclock.epd import epd13in3b
        logger.info("Package import successful")
    except ImportError as e:
        logger.error(f"Package import failed: {e}")
        
        # If that fails, check if the module exists in utils
        utils_module = os.path.join(parent_dir, 'utils', 'epd13in3b.py')
        if os.path.exists(utils_module):
            logger.info(f"Found module in utils: {utils_module}")
            
            # Create symbolic link or copy if needed
            try:
                if not os.path.exists(os.path.join(current_dir, 'epd13in3b.py')):
                    os.symlink(utils_module, os.path.join(current_dir, 'epd13in3b.py'))
                    logger.info("Created symbolic link to utils module")
            except Exception as link_error:
                logger.error(f"Failed to create symbolic link: {link_error}")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    ensure_compatibility()
    print("Compatibility check complete") 