#!/usr/bin/env python3
import os
import json
import logging
import textwrap
from PIL import Image, ImageDraw, ImageFont
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self, config_path='data/config.json'):
        # Load configuration
        self.config = self.load_config(config_path)
        
        # Set up paths
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.font_dir = os.path.join(self.base_dir, 'fonts')
        self.img_dir = os.path.join(self.base_dir, 'images')
        
        # Create directories if they don't exist
        os.makedirs(self.font_dir, exist_ok=True)
        os.makedirs(self.img_dir, exist_ok=True)
        
        # Load fonts - using default if custom fonts are not available
        try:
            self.time_font = ImageFont.truetype(
                os.path.join(self.font_dir, 'OpenSans-Bold.ttf'), 
                self.config.get('font_size', 40) * 2
            )
            self.quote_font = ImageFont.truetype(
                os.path.join(self.font_dir, 'OpenSans-Regular.ttf'), 
                self.config.get('font_size', 40)
            )
            self.source_font = ImageFont.truetype(
                os.path.join(self.font_dir, 'OpenSans-Italic.ttf'), 
                int(self.config.get('font_size', 40) * 0.8)
            )
        except Exception as e:
            logger.warning(f"Error loading custom fonts: {e}. Using default fonts.")
            self.time_font = ImageFont.load_default()
            self.quote_font = ImageFont.load_default()
            self.source_font = ImageFont.load_default()
        
        # Display dimensions - from epd13in3b.py
        self.width = 960
        self.height = 680
        
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            # Return default configuration
            return {
                "update_interval": 600,
                "font_size": 40,
                "show_book_info": True,
                "show_author": True,
                "content_filter": "all",
                "display_brightness": 100
            }
    
    def load_quotes(self, json_path='data/quotes.json'):
        """Load quotes from JSON file"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading quotes: {e}")
            return {}
    
    def get_quote_for_time(self, time_str, quotes_data):
        """Get a quote for the specified time"""
        if time_str in quotes_data:
            quote_data = quotes_data[time_str]
            
            # Handle case when there are multiple quotes for the same time
            if isinstance(quote_data, list):
                # Filter based on content_filter
                if self.config.get('content_filter') == 'sfw':
                    filtered_quotes = [q for q in quote_data if q.get('rating') == 'sfw']
                    if filtered_quotes:
                        return random.choice(filtered_quotes)
                    else:
                        return random.choice(quote_data)  # Fall back if no sfw quotes
                elif self.config.get('content_filter') == 'nsfw':
                    filtered_quotes = [q for q in quote_data if q.get('rating') == 'nsfw']
                    if filtered_quotes:
                        return random.choice(filtered_quotes)
                    else:
                        return random.choice(quote_data)  # Fall back if no nsfw quotes
                else:
                    # All quotes (default)
                    return random.choice(quote_data)
            else:
                # Single quote
                return quote_data
        
        # If no quote for exact time, find closest time
        times = list(quotes_data.keys())
        if not times:
            return None
        
        # Sort times
        times.sort()
        
        # Find closest time - simple linear search
        # Could be optimized with binary search for larger datasets
        closest_time = times[0]
        for t in times:
            if t <= time_str:
                closest_time = t
            else:
                break
        
        return self.get_quote_for_time(closest_time, quotes_data)
    
    def create_image(self, time_str, quote_data):
        """Create an image with the time and quote"""
        if not quote_data:
            logger.error("No quote data provided")
            return None, None
        
        # Create new black and red images
        black_image = Image.new('1', (self.width, self.height), 255)  # 255 = white
        red_image = Image.new('1', (self.width, self.height), 255)    # 255 = white
        
        # Create drawing objects
        black_draw = ImageDraw.Draw(black_image)
        red_draw = ImageDraw.Draw(red_image)
        
        # Draw the time in red at the top
        display_time = quote_data.get('display_time', time_str)
        time_w, time_h = red_draw.textsize(display_time, font=self.time_font)
        red_draw.text(
            ((self.width - time_w) // 2, 40),
            display_time, 
            font=self.time_font, 
            fill=0  # 0 = black/red
        )
        
        # Draw the quote in black
        quote = quote_data.get('quote', '')
        # Wrap the text to fit the width
        wrapped_quote = textwrap.fill(quote, width=50)
        quote_x = 60
        quote_y = 40 + time_h + 60
        black_draw.text(
            (quote_x, quote_y),
            wrapped_quote,
            font=self.quote_font,
            fill=0
        )
        
        # Calculate height of the wrapped quote
        _, quote_text_height = black_draw.multiline_textsize(wrapped_quote, font=self.quote_font)
        
        # Draw book and author info if enabled
        if self.config.get('show_book_info', True):
            book = quote_data.get('book', '')
            source_text = book
            
            if self.config.get('show_author', True):
                author = quote_data.get('author', '')
                if author:
                    source_text += f" — {author}"
            
            source_y = quote_y + quote_text_height + 40
            black_draw.text(
                (self.width - 60 - black_draw.textsize(source_text, font=self.source_font)[0], source_y),
                source_text,
                font=self.source_font,
                fill=0
            )
        
        return black_image, red_image
    
    def generate_and_save(self, time_str):
        """Generate and save images for the given time"""
        quotes_data = self.load_quotes()
        quote_data = self.get_quote_for_time(time_str, quotes_data)
        
        if not quote_data:
            logger.error(f"No quote found for time {time_str}")
            return None, None
        
        black_image, red_image = self.create_image(time_str, quote_data)
        
        if black_image and red_image:
            # Save the images
            black_path = os.path.join(self.img_dir, f"{time_str.replace(':', '_')}_black.bmp")
            red_path = os.path.join(self.img_dir, f"{time_str.replace(':', '_')}_red.bmp")
            
            black_image.save(black_path)
            red_image.save(red_path)
            
            logger.info(f"Generated images for {time_str}")
            return black_path, red_path
        
        return None, None

if __name__ == "__main__":
    import datetime
    
    generator = ImageGenerator()
    
    # Generate image for current time
    now = datetime.datetime.now()
    time_str = now.strftime("%H:%M")
    
    black_path, red_path = generator.generate_and_save(time_str)
    
    if black_path and red_path:
        print(f"Generated: {black_path} and {red_path}") 