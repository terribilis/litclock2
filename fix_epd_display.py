#!/usr/bin/env python3
"""
Helper script to diagnose and fix e-paper display issues.
This creates proper links between utils and package directories.
"""

import os
import sys
import shutil
import logging
import importlib
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('epd_fix')

def check_dependencies():
    """Check if required dependencies are installed"""
    dependencies = ['RPi.GPIO', 'gpiozero', 'spidev', 'PIL']
    missing = []
    
    for dep in dependencies:
        try:
            importlib.import_module(dep)
            logger.info(f"✓ Found dependency: {dep}")
        except ImportError:
            logger.warning(f"✗ Missing dependency: {dep}")
            missing.append(dep)
    
    return missing

def fix_imports():
    """
    Fix the imports by copying files from utils to the package directory
    """
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define source and destination paths
    utils_dir = os.path.join(script_dir, 'utils')
    package_dir = os.path.join(script_dir, 'litclock', 'epd')
    
    # Check if directories exist
    if not os.path.exists(utils_dir):
        logger.error(f"Utils directory not found: {utils_dir}")
        return False
    
    if not os.path.exists(package_dir):
        logger.error(f"Package directory not found: {package_dir}")
        return False
    
    # List files to copy
    files_to_copy = ['epd13in3b.py', 'epdconfig.py']
    
    # Copy each file
    success = True
    for file in files_to_copy:
        source = os.path.join(utils_dir, file)
        dest = os.path.join(package_dir, file)
        
        if not os.path.exists(source):
            logger.error(f"Source file not found: {source}")
            success = False
            continue
        
        try:
            # Make backup of existing file if it exists
            if os.path.exists(dest):
                backup = f"{dest}.bak"
                logger.info(f"Creating backup of {dest} to {backup}")
                shutil.copy2(dest, backup)
            
            # Copy file
            logger.info(f"Copying {source} to {dest}")
            shutil.copy2(source, dest)
            
            # Update import statement if it's the epd13in3b.py file
            if file == 'epd13in3b.py':
                with open(dest, 'r') as f:
                    content = f.read()
                
                # Replace the import statement
                if 'from utils import epdconfig' in content:
                    content = content.replace('from utils import epdconfig', 'from litclock.epd import epdconfig')
                    with open(dest, 'w') as f:
                        f.write(content)
                    logger.info(f"Updated import statement in {dest}")
        
        except Exception as e:
            logger.error(f"Error copying {file}: {e}")
            success = False
    
    return success

def main():
    parser = argparse.ArgumentParser(description='Fix e-paper display issues')
    parser.add_argument('--check', action='store_true', help='Check dependencies only')
    parser.add_argument('--fix', action='store_true', help='Fix imports by copying files')
    args = parser.parse_args()
    
    if not (args.check or args.fix):
        parser.print_help()
        return
    
    if args.check:
        missing = check_dependencies()
        if missing:
            logger.warning("Some dependencies are missing. Install them with:")
            logger.warning(f"pip install {' '.join(missing)}")
        else:
            logger.info("All dependencies are installed.")
    
    if args.fix:
        if fix_imports():
            logger.info("Successfully fixed imports!")
            logger.info("Now run: python -m litclock --test")
        else:
            logger.error("Failed to fix imports. Check the logs for details.")

if __name__ == "__main__":
    main() 