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

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_display():
    """Run a comprehensive test of the e-paper display"""
    try:
        # Import the EPD class from our package
        from litclock.epd import EPD
        
        logger.info("Initializing 13.3-inch e-Paper display")
        epd = EPD()
        
        logger.info("Init and Clear")
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
        black_image = Image.new('1', (epd.width, epd.height), 255)  # 255: white, 0: black
        red_image = Image.new('1', (epd.width, epd.height), 255)    # 255: white, 0: red
        
        draw_black = ImageDraw.Draw(black_image)
        draw_red = ImageDraw.Draw(red_image)
        
        # Draw some text and shapes
        draw_black.text((10, 10), 'Literary Clock Test', font=font35, fill=0)
        draw_red.text((10, 60), '13.3-inch e-Paper (B)', font=font24, fill=0)
        draw_black.text((10, 100), 'Current time: ' + time.strftime('%H:%M:%S'), font=font24, fill=0)
        draw_black.text((10, 140), 'Date: ' + time.strftime('%Y-%m-%d'), font=font24, fill=0)
        
        # Draw a border around the display
        draw_black.rectangle((5, 5, epd.width-5, epd.height-5), outline=0)
        
        # Draw some shapes
        # Black shapes
        draw_black.line((50, 200, 150, 300), fill=0, width=3)
        draw_black.rectangle((200, 200, 300, 300), outline=0)
        draw_black.ellipse((350, 200, 450, 300), outline=0)
        
        # Red shapes
        draw_red.line((500, 200, 600, 300), fill=0, width=3)
        draw_red.rectangle((650, 200, 750, 300), outline=0)
        draw_red.ellipse((800, 200, 900, 300), outline=0)
        
        # Filled shapes
        draw_black.rectangle((200, 350, 300, 450), fill=0)
        draw_red.ellipse((350, 350, 450, 450), fill=0)
        
        # Display the images
        logger.info("Displaying test pattern...")
        epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))
        
        # Wait for 5 seconds
        logger.info("Test pattern will remain for 5 seconds...")
        time.sleep(5)
        
        # Partial update demo
        logger.info("Demonstrating partial updates...")
        for i in range(5):
            # Update a small area with the current time
            draw_black.rectangle((10, 100, 400, 124), fill=255)  # Clear the time area
            draw_black.text((10, 100), 'Current time: ' + time.strftime('%H:%M:%S'), font=font24, fill=0)
            
            # Perform partial update
            epd.display_Partial(epd.getbuffer(black_image), 10, 100, 400, 124)
            time.sleep(1)
        
        # Clear the display when done
        logger.info("Clearing display...")
        epd.Clear()
        
        # Put the display to sleep
        logger.info("Putting display to sleep...")
        epd.sleep()
        
        logger.info("Test completed successfully!")
        return True
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        try:
            from litclock.epd import EPD
            epd = EPD()
            epd.sleep()
        except:
            pass
        return False
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        import traceback
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