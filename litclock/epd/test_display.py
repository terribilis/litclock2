#!/usr/bin/env python3
"""
Test script for the 13.3-inch e-paper display (B).
This script demonstrates various display capabilities.
"""

import os
import sys
import time
import logging
import argparse
from PIL import Image, ImageDraw, ImageFont
import traceback

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add utils directory to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
utils_path = os.path.join(project_root, 'utils')
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)
    logger.debug(f"Added utils path to sys.path: {utils_path}")

# Import and run the compatibility module to ensure paths are set up
try:
    logger.debug("Attempting to import and run compatibility module...")
    from litclock.epd.compatibility import ensure_compatibility
    ensure_compatibility()
    logger.debug("Compatibility setup complete")
except Exception as e:
    logger.warning(f"Compatibility setup failed: {e}, will try direct import")

def get_epd_module():
    """Try multiple ways to import the EPD module"""
    
    # Method 1: Try direct import like the original working script
    try:
        logger.debug("Trying direct import from utils...")
        import epd13in3b
        logger.info("SUCCESS: Imported epd13in3b directly")
        return epd13in3b
    except ImportError as e:
        logger.debug(f"Direct import failed: {e}")
    
    # Method 2: Try package import
    try:
        logger.debug("Trying package import...")
        from litclock.epd import epd13in3b
        logger.info("SUCCESS: Imported epd13in3b from package")
        return epd13in3b
    except ImportError as e:
        logger.debug(f"Package import failed: {e}")
    
    # Method 3: Try sys.path manipulation
    try:
        logger.debug("Trying import after path manipulation...")
        module_path = os.path.join(utils_path, 'epd13in3b.py')
        if os.path.exists(module_path):
            logger.debug(f"Found module at {module_path}")
            
            # If we're on Python 3.5+, use importlib.util
            if sys.version_info >= (3, 5):
                import importlib.util
                spec = importlib.util.spec_from_file_location("epd13in3b", module_path)
                epd13in3b = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(epd13in3b)
                logger.info("SUCCESS: Imported epd13in3b using importlib")
                return epd13in3b
        else:
            logger.error(f"Module file not found at {module_path}")
    except Exception as e:
        logger.debug(f"Import after path manipulation failed: {e}")
    
    # If all methods fail, raise an error
    raise ImportError("Could not import epd13in3b module using any method")

def test_display():
    """Run a comprehensive test of the e-paper display"""
    try:
        # Try to get the EPD module
        try:
            epd13in3b = get_epd_module()
        except ImportError as e:
            logger.error(f"Failed to import epd13in3b: {e}")
            logger.error(f"Current sys.path: {sys.path}")
            return False
        
        logger.info("epd13in3b Demo")
        epd = epd13in3b.EPD()
        
        logger.info("init and Clear")
        epd.init()
        epd.Clear()
        
        # Set up fonts and paths
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        font_dir = os.path.join(base_dir, 'fonts')
        
        # Try to load fonts
        try:
            font_path = os.path.join(font_dir, 'OpenSans-Regular.ttf')
            if os.path.exists(font_path):
                font24 = ImageFont.truetype(font_path, 24)
                font18 = ImageFont.truetype(font_path, 18)
                font35 = ImageFont.truetype(font_path, 35)
            else:
                logger.warning(f"Font file not found at {font_path}, using default font")
                font24 = ImageFont.load_default()
                font18 = ImageFont.load_default()
                font35 = ImageFont.load_default()
        except Exception as e:
            logger.warning(f"Error loading fonts: {e}")
            font24 = ImageFont.load_default()
            font18 = ImageFont.load_default()
            font35 = ImageFont.load_default()
        
        # Drawing on the Horizontal image - following exact same pattern as working example
        logger.info("Drawing on the Horizontal image...")
        HBlackimage = Image.new('1', (epd.width, epd.height), 255)  # 255: white, 0: black
        HRedimage = Image.new('1', (epd.width, epd.height), 255)    # 255: white, 0: red
        
        drawblack = ImageDraw.Draw(HBlackimage)
        drawred = ImageDraw.Draw(HRedimage)
        
        # Draw exactly the same test pattern as the working example
        drawblack.text((10, 0), 'hello world', font=font24, fill=0)
        drawred.text((10, 20), '13.3inch e-Paper (B)', font=font24, fill=0)
        drawblack.text((150, 0), 'Waveshare Electronics', font=font24, fill=0)
        drawred.line((20, 50, 70, 100), fill=0)
        drawblack.line((70, 50, 20, 100), fill=0)
        drawred.rectangle((20, 50, 70, 100), outline=0)
        drawblack.line((165, 50, 165, 100), fill=0)
        drawred.line((140, 75, 190, 75), fill=0)
        drawblack.arc((140, 50, 190, 100), 0, 360, fill=0)
        drawred.rectangle((80, 50, 130, 100), fill=0)
        drawblack.chord((200, 50, 250, 100), 0, 360, fill=0)
        
        # Use display_Base as the working example does
        logger.info("Displaying test pattern...")
        epd.display_Base(epd.getbuffer(HBlackimage), epd.getbuffer(HRedimage))
        time.sleep(2)
        
        # Partial update demo - exactly as in the working example
        logger.info("Demonstrating partial updates (showing time)...")
        num = 0
        while True:
            drawblack.rectangle((0, 110, 120, 150), fill=255)
            drawblack.text((10, 120), time.strftime('%H:%M:%S'), font=font24, fill=0)
            epd.display_Partial(epd.getbuffer(HBlackimage), 0, 110, 120, 160)
            num = num + 1
            if num == 10:
                break
        
        # Clean up exactly as in the working example 
        logger.info("Clear...")
        epd.init()
        epd.Clear()
        
        # Put the display to sleep
        logger.info("Goto Sleep...")
        epd.sleep()
        
        logger.info("Test completed successfully!")
        return True
        
    except KeyboardInterrupt:
        logger.info("ctrl + c:")
        try:
            # Use the same module exit as the original script
            epd13in3b = get_epd_module()
            epd13in3b.epdconfig.module_exit(cleanup=True)
        except:
            logger.error("Failed to clean up")
        exit()
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Test the e-paper display')
    parser.add_argument('--debug', action='store_true', help='Enable verbose debug output')
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if test_display():
        print("Display test completed successfully!")
    else:
        print("Display test failed or was interrupted.")
        sys.exit(1)

if __name__ == "__main__":
    main() 