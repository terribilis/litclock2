#!/usr/bin/env python3
import os
import sys
import json
import time
import datetime
import logging
import argparse
from PIL import Image

# Set up logging
logger = logging.getLogger(__name__)

class LiteraryClock:
    def __init__(self, config_path='data/config.json'):
        # Import here to avoid circular imports
        from litclock.epd import EPD
        from litclock.utils.image_generator import ImageGenerator

        self.config_path = config_path
        self.config = self.load_config()
        
        # Set up paths
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.img_dir = os.path.join(self.base_dir, 'images')
        os.makedirs(self.img_dir, exist_ok=True)
        
        # Initialize e-paper display
        try:
            self.epd = EPD()
            if self.epd.init() != 0:
                logger.error("e-Paper init failed")
                sys.exit(1)
            logger.info("e-Paper initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing e-Paper: {e}")
            sys.exit(1)
        
        # Initialize image generator
        self.image_generator = ImageGenerator(config_path)
        
        # Flag to track if we need to regenerate JSON from CSV
        self.should_regenerate_json = False
        
        # Track partial refresh count
        self.partial_refresh_count = 0
        
        # Check if JSON needs to be generated
        json_path = os.path.join(self.base_dir, 'data', 'quotes.json')
        if not os.path.exists(json_path):
            self.regenerate_json()
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"Configuration loaded: {config}")
                return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            # Return default configuration
            default_config = {
                "update_interval": 600,
                "font_size": 40,
                "show_book_info": True,
                "show_author": True,
                "content_filter": "all",
                "display_brightness": 100,
                "partial_refresh_count": 10  # Number of partial refreshes before a full refresh
            }
            logger.info(f"Using default configuration: {default_config}")
            return default_config
    
    def save_config(self, config):
        """Save configuration to JSON file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            self.config = config
            logger.info(f"Configuration saved: {config}")
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def regenerate_json(self):
        """Regenerate the JSON file from the CSV"""
        from litclock.utils.csv_converter import convert_csv_to_json
        
        logger.info("Regenerating JSON from CSV")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(base_dir, 'data', 'litclock_annotated.csv')
        json_path = os.path.join(base_dir, 'data', 'quotes.json')
        
        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found: {csv_path}")
            return False
        
        result = convert_csv_to_json(csv_path, json_path)
        self.should_regenerate_json = False
        return result
    
    def update_display(self):
        """Update the e-paper display with the current time's quote"""
        try:
            # Get current time
            now = datetime.datetime.now()
            time_str = now.strftime("%H:%M")
            logger.info(f"Updating display for time: {time_str}")
            
            # Generate images for the current time
            black_path, red_path = self.image_generator.generate_and_save(time_str)
            
            if not black_path or not red_path:
                logger.error("Failed to generate images")
                return False
            
            # Load the images
            black_image = Image.open(black_path)
            red_image = Image.open(red_path)
            
            # Convert to e-paper format
            black_buffer = self.epd.getbuffer(black_image)
            red_buffer = self.epd.getbuffer(red_image)
            
            # Check if we need a full refresh
            partial_refresh_count = self.config.get('partial_refresh_count', 10)
            if self.partial_refresh_count >= partial_refresh_count:
                logger.info("Performing full refresh after partial refresh count reached")
                self.epd.display(black_buffer, red_buffer)
                self.partial_refresh_count = 0
            else:
                # Use partial refresh
                logger.info(f"Performing partial refresh ({self.partial_refresh_count + 1}/{partial_refresh_count})")
                # For partial refresh, we only update the black channel
                self.epd.display_Partial(black_buffer, 0, 0, self.epd.width, self.epd.height)
                self.partial_refresh_count += 1
            
            logger.info("Display updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating display: {e}")
            return False
    
    def run(self):
        """Run the clock in a loop"""
        last_update = 0
        update_interval = self.config.get('update_interval', 600)  # Default to 10 minutes
        
        try:
            while True:
                current_time = time.time()
                
                # Check if config has been updated
                new_config = self.load_config()
                if new_config != self.config:
                    logger.info("Config changed, updating settings")
                    self.config = new_config
                    update_interval = self.config.get('update_interval', 600)
                
                # Check if we need to regenerate JSON
                if self.should_regenerate_json:
                    self.regenerate_json()
                
                # Update the display if enough time has passed
                if current_time - last_update >= update_interval:
                    if self.update_display():
                        last_update = current_time
                    else:
                        # If update failed, wait a shorter time before retrying
                        time.sleep(60)
                        continue
                
                # Sleep for a bit to avoid CPU usage
                time.sleep(5)
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down")
            self.shutdown()
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown of the e-paper display"""
        try:
            logger.info("Shutting down e-paper display")
            self.epd.sleep()
        except Exception as e:
            logger.error(f"Error shutting down e-paper: {e}")

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("litclock.log"),
            logging.StreamHandler()
        ]
    )
    
    parser = argparse.ArgumentParser(description='Literary Clock for e-Paper Display')
    parser.add_argument('--config', default='data/config.json', help='Path to config file')
    parser.add_argument('--regenerate', action='store_true', help='Regenerate JSON from CSV')
    args = parser.parse_args()
    
    clock = LiteraryClock(args.config)
    
    if args.regenerate:
        clock.regenerate_json()
    
    clock.run()

if __name__ == "__main__":
    main() 