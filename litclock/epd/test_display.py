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
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import and run the compatibility module to ensure paths are set up
try:
    from litclock.epd.compatibility import ensure_compatibility
    ensure_compatibility()
except Exception as e:
    logger.warning(f"Compatibility setup failed: {e}, will try direct import")

def test_display():
    """Run a comprehensive test of the e-paper display"""
    try:
        # Try to find the module in multiple ways - first use direct import like the working example
        try:
            # Add utils directory to path if not already there
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            utils_path = os.path.join(project_root, 'utils')
            if utils_path not in sys.path:
                sys.path.insert(0, utils_path)
                
            # Try to import like in the original working script
            try:
                import epd13in3b
                logger.info("Imported epd13in3b directly")
            except ImportError:
                # Fall back to package import
                from litclock.epd import epd13in3b
                logger.info("Imported epd13in3b from package")
        except ImportError as e:
            logger.error(f"Failed to import epd13in3b: {e}")
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
            if 'epd13in3b' in locals():
                epd13in3b.epdconfig.module_exit(cleanup=True)
            else:
                from litclock.epd import epd13in3b
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
    args = parser.parse_args()
    
    if test_display():
        print("Display test completed successfully!")
    else:
        print("Display test failed or was interrupted.")
        sys.exit(1)

if __name__ == "__main__":
    main() 