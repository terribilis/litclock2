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

def test_display():
    """Run a comprehensive test of the e-paper display"""
    try:
        # Import the specific EPD module
        from litclock.epd import epd13in3b
        
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
        
        # Drawing on the Horizontal image
        logger.info("Drawing test patterns...")
        HBlackimage = Image.new('1', (epd.width, epd.height), 255)  # 255: white, 0: black
        HRedimage = Image.new('1', (epd.width, epd.height), 255)    # 255: white, 0: red
        
        drawblack = ImageDraw.Draw(HBlackimage)
        drawred = ImageDraw.Draw(HRedimage)
        
        # Draw some text and shapes - following the original test
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
        
        # Important: Use display_Base instead of display
        logger.info("Displaying test pattern...")
        epd.display_Base(epd.getbuffer(HBlackimage), epd.getbuffer(HRedimage))
        
        # Wait for 2 seconds
        time.sleep(2)
        
        # Partial update demo
        logger.info("Demonstrating partial updates...")
        num = 0
        while True:
            drawblack.rectangle((0, 110, 120, 150), fill=255)
            drawblack.text((10, 120), time.strftime('%H:%M:%S'), font=font24, fill=0)
            epd.display_Partial(epd.getbuffer(HBlackimage), 0, 110, 120, 160)
            num = num + 1
            if num == 10:
                break
        
        # Clear the display when done
        logger.info("Clearing display...")
        epd.init()
        epd.Clear()
        
        # Put the display to sleep
        logger.info("Putting display to sleep...")
        epd.sleep()
        
        logger.info("Test completed successfully!")
        return True
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        try:
            from litclock.epd import epd13in3b
            epd13in3b.epdconfig.module_exit(cleanup=True)
        except:
            pass
        return False
        
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