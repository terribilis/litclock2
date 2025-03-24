#!/usr/bin/env python3
"""
Compatibility module for e-paper display
This ensures that both the old direct import method and the new package method work.
"""

import os
import sys
import logging
import importlib.util

# Add the current directory to sys.path to enable direct imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))  # Get to project root
sys.path.insert(0, parent_dir)  # Add project root to path
sys.path.insert(0, os.path.join(parent_dir, 'utils'))  # Add utils directory to path

# Configure logging
logger = logging.getLogger(__name__)

def check_gpio_libraries():
    """Check which GPIO libraries are available"""
    libraries = {
        'gpiozero': False,
        'RPi.GPIO': False
    }
    
    for lib in libraries.keys():
        try:
            importlib.import_module(lib)
            libraries[lib] = True
            logger.info(f"Found GPIO library: {lib}")
        except ImportError:
            logger.warning(f"GPIO library not found: {lib}")
    
    return libraries

def ensure_compatibility():
    """
    Ensure that both import methods work by setting up the proper paths
    and creating any necessary symbolic links.
    """
    # Check which GPIO libraries are available
    libraries = check_gpio_libraries()
    
    # First, try importing using the package structure
    try:
        from litclock.epd import epd13in3b
        logger.info("Package import successful")
    except ImportError as e:
        logger.error(f"Package import failed: {e}")
        
        # If that fails, check if the module exists in utils
        utils_module = os.path.join(parent_dir, 'utils', 'epd13in3b.py')
        utils_config = os.path.join(parent_dir, 'utils', 'epdconfig.py')
        
        if os.path.exists(utils_module) and os.path.exists(utils_config):
            logger.info(f"Found module in utils: {utils_module}")
            
            # Create symbolic links or copy if needed
            try:
                # Link or copy the main module
                if not os.path.exists(os.path.join(current_dir, 'epd13in3b.py')):
                    if hasattr(os, 'symlink'):
                        os.symlink(utils_module, os.path.join(current_dir, 'epd13in3b.py'))
                        logger.info("Created symbolic link to utils epd13in3b.py module")
                    else:
                        # On platforms that don't support symlinks (e.g., Windows)
                        import shutil
                        shutil.copy2(utils_module, os.path.join(current_dir, 'epd13in3b.py'))
                        logger.info("Copied utils epd13in3b.py module")
                
                # Link or copy the config module
                if not os.path.exists(os.path.join(current_dir, 'epdconfig.py')):
                    if hasattr(os, 'symlink'):
                        os.symlink(utils_config, os.path.join(current_dir, 'epdconfig.py'))
                        logger.info("Created symbolic link to utils epdconfig.py module")
                    else:
                        # On platforms that don't support symlinks
                        import shutil
                        shutil.copy2(utils_config, os.path.join(current_dir, 'epdconfig.py'))
                        logger.info("Copied utils epdconfig.py module")
            except Exception as link_error:
                logger.error(f"Failed to create symbolic link or copy: {link_error}")
        else:
            logger.error(f"Could not find required modules in utils directory")
            
    # Verify the module can be imported
    try:
        import litclock.epd.epd13in3b
        logger.info("Successfully imported epd13in3b module")
        return True
    except ImportError as e:
        logger.error(f"Still unable to import epd13in3b module: {e}")
        return False

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    if ensure_compatibility():
        print("Compatibility check complete - all modules available")
    else:
        print("Compatibility check failed - some modules could not be imported")
        sys.exit(1) 