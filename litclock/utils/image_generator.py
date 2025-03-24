#!/usr/bin/env python3
import os
import json
import logging
import textwrap
from PIL import Image, ImageDraw, ImageFont
import random
import re
import csv

# Configure logging - make it more detailed
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self, config_path='data/config.json', debug=False):
        # Enable debug mode for more verbose output
        self.debug = debug
        if self.debug:
            logger.setLevel(logging.DEBUG)
        
        # Load configuration
        self.config = self.load_config(config_path)
        
        # Set up paths
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.font_dir = os.path.join(self.base_dir, 'fonts')
        self.img_dir = os.path.join(self.base_dir, 'images')
        
        # Create directories if they don't exist
        os.makedirs(self.font_dir, exist_ok=True)
        os.makedirs(self.img_dir, exist_ok=True)
        
        # Load fonts - using default if custom fonts are not available
        try:
            # Keep track of available fonts
            self.fonts = {}
            
            # Normal font for quote text
            self.fonts['normal'] = {}
            # Bold font for highlighted time in quote
            self.fonts['bold'] = {}
            # Font for metadata (author, title)
            self.fonts['meta'] = {}
            
            # Get a larger base font for scaling
            try:
                # Try to load system fonts - testing multiple common fonts
                system_fonts = [
                    # macOS/Unix system fonts
                    '/System/Library/Fonts/Helvetica.ttc',
                    '/System/Library/Fonts/Geneva.ttf',
                    '/Library/Fonts/Arial.ttf',
                    # Windows fonts
                    'C:\\Windows\\Fonts\\arial.ttf',
                    # Linux fonts
                    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                    # Default last resort
                    'DejaVuSans.ttf'
                ]
                
                # Try each font until one works
                base_font_normal = None
                base_font_bold = None
                
                for font_path in system_fonts:
                    if os.path.exists(font_path):
                        try:
                            base_font_normal = ImageFont.truetype(font_path, 16)
                            # Try bold version if available (same file for TTC)
                            base_font_bold = ImageFont.truetype(font_path, 16)
                            logger.info(f"Successfully loaded system font: {font_path}")
                            break
                        except:
                            continue
                
                # If we couldn't load any system font, fall back to default
                if base_font_normal is None:
                    raise Exception("No system fonts found")
                    
            except Exception as font_ex:
                # Fall back to default
                logger.warning(f"Could not load system fonts: {font_ex}, using basic default font")
                base_font_normal = ImageFont.load_default()
                base_font_bold = base_font_normal
            
            # Store fonts at different sizes
            for size in range(16, 201, 4):
                try:
                    # For TrueType/OpenType fonts that support direct sizing
                    if base_font_normal != ImageFont.load_default():
                        self.fonts['normal'][size] = ImageFont.truetype(font_path, size)
                        self.fonts['bold'][size] = ImageFont.truetype(font_path, size)
                        self.fonts['meta'][size] = ImageFont.truetype(font_path, size)
                        continue
                except:
                    pass
                
                # Fallback to font_variant method
                try:
                    font_normal = base_font_normal.font_variant(size=size)
                    font_bold = base_font_bold.font_variant(size=size)
                    
                    if font_normal:
                        self.fonts['normal'][size] = font_normal
                        self.fonts['bold'][size] = font_bold
                        self.fonts['meta'][size] = font_normal
                        continue
                except:
                    pass
                
                # If font_variant isn't supported and direct sizing failed, use base font
                self.fonts['normal'][size] = base_font_normal
                self.fonts['bold'][size] = base_font_bold
                self.fonts['meta'][size] = base_font_normal
                logger.warning(f"Font scaling not supported for size {size}, using base font")
            
            if self.debug:
                logger.debug(f"Loaded fonts in sizes: {sorted(self.fonts['normal'].keys())}")
            
        except Exception as e:
            logger.warning(f"Error loading custom fonts: {e}. Using default fonts.")
            # Create fonts with different apparent sizes by using scaling factor for drawing
            self.fonts = {'normal': {}, 'bold': {}, 'meta': {}}
            
            # Get a larger base font for scaling
            try:
                # Try to load system fonts - testing multiple common fonts
                system_fonts = [
                    # macOS/Unix system fonts
                    '/System/Library/Fonts/Helvetica.ttc',
                    '/System/Library/Fonts/Geneva.ttf',
                    '/Library/Fonts/Arial.ttf',
                    # Windows fonts
                    'C:\\Windows\\Fonts\\arial.ttf',
                    # Linux fonts
                    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                    # Default last resort
                    'DejaVuSans.ttf'
                ]
                
                # Try each font until one works
                base_font_normal = None
                base_font_bold = None
                
                for font_path in system_fonts:
                    if os.path.exists(font_path):
                        try:
                            base_font_normal = ImageFont.truetype(font_path, 16)
                            # Try bold version if available (same file for TTC)
                            base_font_bold = ImageFont.truetype(font_path, 16)
                            logger.info(f"Successfully loaded system font: {font_path}")
                            break
                        except:
                            continue
                
                # If we couldn't load any system font, fall back to default
                if base_font_normal is None:
                    raise Exception("No system fonts found")
                    
            except Exception as font_ex:
                # Fall back to default
                logger.warning(f"Could not load system fonts: {font_ex}, using basic default font")
                base_font_normal = ImageFont.load_default()
                base_font_bold = base_font_normal
            
            # Store fonts at different sizes
            for size in range(16, 201, 4):
                try:
                    # For TrueType/OpenType fonts that support direct sizing
                    if base_font_normal != ImageFont.load_default():
                        self.fonts['normal'][size] = ImageFont.truetype(font_path, size)
                        self.fonts['bold'][size] = ImageFont.truetype(font_path, size)
                        self.fonts['meta'][size] = ImageFont.truetype(font_path, size)
                        continue
                except:
                    pass
                
                # Fallback to font_variant method
                try:
                    font_normal = base_font_normal.font_variant(size=size)
                    font_bold = base_font_bold.font_variant(size=size)
                    
                    if font_normal:
                        self.fonts['normal'][size] = font_normal
                        self.fonts['bold'][size] = font_bold
                        self.fonts['meta'][size] = font_normal
                        continue
                except:
                    pass
                
                # If font_variant isn't supported and direct sizing failed, use base font
                self.fonts['normal'][size] = base_font_normal
                self.fonts['bold'][size] = base_font_bold
                self.fonts['meta'][size] = base_font_normal
                logger.warning(f"Font scaling not supported for size {size}, using base font")
            
        # Display dimensions from epd13in3b.py
        self.width = 960
        self.height = 680
        logger.info(f"Display dimensions: {self.width}x{self.height}")
        
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
    
    def load_quotes(self):
        """Load quotes from CSV file"""
        quotes_data = {}
        
        try:
            # Check if quotes file exists
            quotes_file = self.config.get('quotes_file', '')
            if not os.path.exists(quotes_file):
                logger.warning(f"Quotes file not found: {quotes_file}")
                # Look for quotes file in default locations
                potential_paths = [
                    os.path.join(os.path.dirname(__file__), '../../data/quotes.csv'),
                    os.path.join(os.path.dirname(__file__), '../data/quotes.csv'),
                    os.path.join(os.path.dirname(__file__), 'data/quotes.csv'),
                    'data/quotes.csv',
                ]
                
                for path in potential_paths:
                    if os.path.exists(path):
                        quotes_file = path
                        logger.info(f"Found quotes file at: {quotes_file}")
                        break
            
            if not quotes_file or not os.path.exists(quotes_file):
                logger.error("No quotes file found")
                return {}
            
            # Read quotes from CSV
            with open(quotes_file, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f, delimiter='|')
                for row in csv_reader:
                    if len(row) >= 5:  # Ensure we have at least time, timestring, quote, title, author
                        time_str = row[0].strip()
                        timestring = row[1].strip()
                        quote = row[2].strip()
                        title = row[3].strip()
                        author = row[4].strip()
                        rating = row[5].strip() if len(row) > 5 else "sfw"
                        
                        quote_entry = {
                            'time': time_str,
                            'display_time': timestring,
                            'quote': quote,
                            'title': title,
                            'author': author,
                            'rating': rating
                        }
                        
                        # Add quote to appropriate time entry
                        if time_str not in quotes_data:
                            quotes_data[time_str] = []
                        quotes_data[time_str].append(quote_entry)
            
            logger.info(f"Loaded {sum(len(quotes) for quotes in quotes_data.values())} quotes for {len(quotes_data)} times")
            
            return quotes_data
        except Exception as e:
            logger.error(f"Error loading quotes: {e}")
            return {}
    
    def get_quote_for_time(self, time_str, quotes_data=None):
        """Get a quote for a specific time"""
        if not quotes_data:
            quotes_data = self.load_quotes()
            
        # Find quotes for this time
        try:
            time_quotes = quotes_data.get(time_str, [])
            if time_quotes:
                return random.choice(time_quotes)
        except Exception as e:
            logger.error(f"Error getting quote for time {time_str}: {e}")
        
        return None
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width, similar to provided example"""
        words = text.split()
        lines = ['']
        
        for word in words:
            line = f'{lines[-1]} {word}'.strip()
            # Get line width
            line_width = font.getlength(line)
            
            if line_width <= max_width:
                lines[-1] = line
            else:
                if self.debug:
                    logger.debug(f"Line too wide ({line_width}px > {max_width}px): '{line}', wrapping to new line")
                lines.append(word)
        
        wrapped_text = '\n'.join(lines)
        if self.debug:
            logger.debug(f"Wrapped text into {len(lines)} lines")
        
        return wrapped_text
    
    def get_line_height(self, font):
        """Calculate appropriate line height based on font size"""
        # For default font which doesn't scale properly
        if font == ImageFont.load_default():
            # Get the approximate font size from our fonts dictionary lookup
            # This is a workaround since default font doesn't expose its size
            for size, size_font in self.fonts['normal'].items():
                if font == size_font:
                    return int(size * 1.2)  # Add 20% spacing
            
            # If we're here, we have a default font but don't know its size
            # Try to infer from where it's being used
            try:
                for key in self.fonts:
                    for size, size_font in self.fonts[key].items():
                        if font == size_font:
                            return int(size * 1.2)
            except:
                pass
            
            # Final fallback for default font - scale based on font size from key
            # Use 12px as minimum, but try to scale based on provided font size if possible
            try:
                # If this is a font from our dictionary with default fallback
                for key in self.fonts:
                    for size in self.fonts[key]:
                        if self.fonts[key][size] == font:
                            return int(size * 1.2)
            except:
                pass
            
            # If we got here, we have to guess - use a larger default value
            # Since we're trying to use larger fonts in general, use a higher value
            return 48  # Assume a medium-large default font size
        
        # For custom fonts, use their actual metrics
        # Get font size by estimating from measuring capital 'M'
        try:
            font_size = font.size
            return int(font_size * 1.2)  # Add 20% spacing between lines
        except:
            # Fallback - use font metrics if size not available
            try:
                (left, top, right, bottom) = font.getbbox("Ay")  # Use characters with ascenders and descenders
                height = bottom - top
                return int(height * 1.2)  # Add 20% spacing between lines
            except:
                # Final fallback - try to determine a reasonable size
                # Measure the height of a capital letter with ascender and descender
                try:
                    ascent = font.getbbox("A")[3]
                    descent = font.getbbox("y")[3] - font.getbbox("y")[1]
                    return int((ascent + descent) * 1.2)
                except:
                    # Absolute final fallback for unknown fonts
                    return 48  # Use a larger default value
    
    def calculate_optimal_font_size(self, text, display_time, max_width, max_height, metadata_height=0):
        """Calculate optimal font size to fill the available space"""
        # Create a dummy image for measurements
        dummy_img = Image.new('1', (1, 1), 255)
        dummy_draw = ImageDraw.Draw(dummy_img)
        
        # Reserve space for metadata
        available_height = max_height - metadata_height - 80  # 40px padding on top and bottom
        available_width = max_width - 80  # 40px padding on each side
        
        logger.info(f"Available space for quote: {available_width}x{available_height}px (after reserving {metadata_height}px for metadata)")
        
        # Try fonts from large to small
        font_sizes = sorted(self.fonts['normal'].keys(), reverse=True)
        
        # Target line count - aim to have at least 4-5 lines to fill vertical space
        min_line_count = 3
        
        # We'll track the best font size that fits and uses space efficiently
        best_size = None
        best_usage = 0  # Percentage of vertical space used (0-1)
        best_wrapped_text = None
        
        for size in font_sizes:
            normal_font = self.fonts['normal'][size]
            
            # Wrap the text with current font size
            wrapped_text = self.wrap_text(text, normal_font, available_width)
            
            # Calculate height using proper line height calculation
            line_count = wrapped_text.count('\n') + 1
            # Use a line height based on font size rather than font metrics
            # This helps with default fonts that don't scale properly
            line_height = int(size * 1.2)  # 20% spacing
            total_height = line_count * line_height
            
            logger.info(f"Trying font size {size}px: {line_count} lines, line height {line_height}px, total height {total_height}px")
            
            # If it fits, calculate how efficiently it uses space
            if total_height <= available_height:
                # Calculate space usage (as percentage of available height)
                usage = total_height / available_height
                
                logger.info(f"Font size {size}px fits with {usage:.2%} vertical space usage")
                
                # If this is our first valid size or it uses space better than previous best
                if best_size is None or (usage > best_usage and line_count >= min_line_count):
                    best_size = size
                    best_usage = usage
                    best_wrapped_text = wrapped_text
                    logger.info(f"New best font size: {size}px with {usage:.2%} space usage")
                
                # If we have a good size that fills at least 85% of space with multiple lines, stop here
                if usage > 0.85 and line_count >= min_line_count:
                    logger.info(f"Selected font size: {size}px (good balance of size and space usage: {usage:.2%})")
                    return size, wrapped_text
            else:
                logger.info(f"Font size {size}px too large (height {total_height}px > available {available_height}px)")
        
        # If we found a size that fits
        if best_size is not None:
            logger.info(f"Selected best font size: {best_size}px (space usage: {best_usage:.2%})")
            return best_size, best_wrapped_text
        
        # If we get here, use the smallest size
        smallest_size = min(font_sizes)
        logger.info(f"Using smallest font size: {smallest_size}px (no size fits perfectly)")
        return smallest_size, self.wrap_text(text, self.fonts['normal'][smallest_size], available_width)
    
    def draw_quote_with_highlighted_time(self, black_draw, red_draw, position, text, time_string, normal_font, bold_font, override_line_height=None):
        """Draw the quote with the time string highlighted in bold/red"""
        x, y = position
        logger.info(f"Drawing quote at position ({x}, {y})")
        
        # Get proper line height
        if override_line_height:
            line_height = override_line_height
            logger.info(f"Using override line height: {line_height}px")
        else:
            line_height = self.get_line_height(normal_font)
            logger.info(f"Line height: {line_height}px")
        
        # Add debug information about font
        if hasattr(normal_font, 'size'):
            logger.info(f"Font size attribute: {normal_font.size}px")
        try:
            bbox = normal_font.getbbox("Ay")
            logger.info(f"Font bounding box: {bbox}")
        except Exception as e:
            logger.info(f"Could not get font bounding box: {e}")
        # Dump font object details for debugging
        logger.info(f"Font object: {normal_font}")
        
        # Look for the time string in the text (case insensitive)
        try:
            time_lower = time_string.lower()
            text_lower = text.lower()
            
            # Get a larger font for the time string (approximately 20% larger)
            # Find the current font size
            current_size = None
            for size, font in self.fonts['normal'].items():
                if font == normal_font:
                    current_size = size
                    break
            
            # If we found the current size, get a larger font for time string
            if current_size:
                # Calculate 20% larger size
                larger_size = int(current_size * 1.2)
                # Find the closest available larger size
                available_sizes = sorted(self.fonts['bold'].keys())
                larger_sizes = [s for s in available_sizes if s >= larger_size]
                if larger_sizes:
                    time_font_size = min(larger_sizes)
                    time_font = self.fonts['bold'][time_font_size]
                    logger.info(f"Using larger font size for time: {time_font_size}px (original: {current_size}px)")
                else:
                    # If no larger size is available, use the largest available
                    time_font_size = max(available_sizes)
                    time_font = self.fonts['bold'][time_font_size]
                    logger.info(f"Using largest available font for time: {time_font_size}px")
            else:
                # Fall back to bold font if we can't determine sizes
                time_font = bold_font
                logger.info("Couldn't determine font size, using regular bold font for time")
            
            # Check if time string exists in the quote
            if time_lower in text_lower:
                # Find all instances of the time string
                start_idx = text_lower.find(time_lower)
                end_idx = start_idx + len(time_string)
                
                logger.info(f"Time string '{time_string}' found in quote at position {start_idx}-{end_idx}")
                
                # Get the actual case from the original text
                actual_time_text = text[start_idx:end_idx]
                
                # Split text into lines for processing
                lines = text.split('\n')
                current_pos = 0
                curr_y = y
                
                # Process each line to find which contains the time
                for line_idx, line in enumerate(lines):
                    line_len = len(line)
                    
                    # Check if this line contains the time string (or part of it)
                    if current_pos <= start_idx < current_pos + line_len + 1:  # +1 for newline
                        # This line contains the start of the time string
                        line_start_idx = start_idx - current_pos
                        line_end_idx = min(end_idx - current_pos, line_len)
                        
                        # Text before time string in this line
                        if line_start_idx > 0:
                            before_time = line[:line_start_idx]
                            black_draw.text((x, curr_y), before_time, fill=0, font=normal_font)
                            x_offset = normal_font.getlength(before_time)
                        else:
                            x_offset = 0
                        
                        # Time string in this line - use black_draw with larger time_font
                        time_part = line[line_start_idx:line_end_idx]
                        # Adjust y position to vertically center the larger font with the normal text
                        if time_font != bold_font:
                            # Calculate vertical adjustment to align baselines
                            normal_height = normal_font.getbbox("Ay")[3]
                            time_height = time_font.getbbox("Ay")[3]
                            y_offset = max(0, (normal_height - time_height) // 2)
                            black_draw.text((x + x_offset, curr_y - y_offset), time_part, fill=0, font=time_font)
                        else:
                            black_draw.text((x + x_offset, curr_y), time_part, fill=0, font=time_font)
                        x_offset += time_font.getlength(time_part)
                        
                        # Text after time string in this line
                        if line_end_idx < line_len:
                            after_time = line[line_end_idx:]
                            black_draw.text((x + x_offset, curr_y), after_time, fill=0, font=normal_font)
                    
                    # Lines that don't contain any part of the time string
                    elif current_pos + line_len <= start_idx or current_pos >= end_idx:
                        black_draw.text((x, curr_y), line, fill=0, font=normal_font)
                    
                    # This line contains continuation of the time string from previous line
                    elif current_pos < end_idx:
                        line_end_idx = min(end_idx - current_pos, line_len)
                        
                        # Time part at beginning of this line
                        time_part = line[:line_end_idx]
                        # Adjust y position for larger font
                        if time_font != bold_font:
                            normal_height = normal_font.getbbox("Ay")[3]
                            time_height = time_font.getbbox("Ay")[3]
                            y_offset = max(0, (normal_height - time_height) // 2)
                            black_draw.text((x, curr_y - y_offset), time_part, fill=0, font=time_font)
                        else:
                            black_draw.text((x, curr_y), time_part, fill=0, font=time_font)
                        x_offset = time_font.getlength(time_part)
                        
                        # Text after time string in this line
                        if line_end_idx < line_len:
                            after_time = line[line_end_idx:]
                            black_draw.text((x + x_offset, curr_y), after_time, fill=0, font=normal_font)
                    
                    # Move down to next line
                    curr_y += line_height
                    current_pos += line_len + 1  # +1 for newline character
            else:
                # Time string not in text, just draw normally
                logger.info(f"Time string '{time_string}' NOT found in quote, drawing as regular text")
                # Use the calculated line height for proper spacing
                line_spacing = max(0, line_height - normal_font.getbbox("A")[3])
                black_draw.multiline_text((x, y), text, fill=0, font=normal_font, spacing=line_spacing)
        except Exception as e:
            logger.error(f"Error highlighting time in quote: {e}")
            # Fallback to normal rendering
            black_draw.multiline_text((x, y), text, fill=0, font=normal_font, spacing=line_height-10)
    
    def draw_debug_info(self, black_draw, red_draw, metadata_height, font_size, padding):
        """Draw debug information directly on the image"""
        if not self.debug:
            return
        
        # Use a small font for debug information
        debug_font = self.fonts['normal'].get(16, ImageFont.load_default())
        
        # Draw available area boundary for quote (880x626)
        # Rectangle for the quote area
        quote_area = [
            padding, padding,  # Top left
            self.width - padding, self.height - padding - metadata_height  # Bottom right
        ]
        black_draw.rectangle(quote_area, outline=0, width=1)
        
        # Label the quote area with dimensions
        quote_width = self.width - 2 * padding
        quote_height = self.height - 2 * padding - metadata_height
        area_label = f"Quote area: {quote_width}x{quote_height}px, Font: {font_size}px"
        black_draw.text((padding + 5, padding + 5), area_label, fill=0, font=debug_font)
        
        # Draw the metadata area
        if metadata_height > 0:
            metadata_area = [
                padding, self.height - padding - metadata_height,  # Top left
                self.width - padding, self.height - padding  # Bottom right
            ]
            black_draw.rectangle(metadata_area, outline=0, width=1)
            
            # Label the metadata area
            meta_label = f"Metadata area: {quote_width}x{metadata_height}px"
            black_draw.text(
                (padding + 5, self.height - padding - metadata_height + 5),
                meta_label, 
                fill=0, 
                font=debug_font
            )
        
        # Draw a grid with 100px spacing
        for x in range(0, self.width, 100):
            # Vertical line
            black_draw.line([(x, 0), (x, self.height)], fill=0, width=1)
            # Label
            if x > 0:
                black_draw.text((x + 2, 2), str(x), fill=0, font=debug_font)
        
        for y in range(0, self.height, 100):
            # Horizontal line
            black_draw.line([(0, y), (self.width, y)], fill=0, width=1)
            # Label
            if y > 0:
                black_draw.text((2, y + 2), str(y), fill=0, font=debug_font)
    
    def create_image(self, quote_data, debug=False):
        """Create images with quotes and time information"""
        # Extract quote data
        quote = quote_data.get('quote', '')
        author = quote_data.get('author', '')
        book = quote_data.get('title', '')  # 'title' in CSV, 'book' in dictionaries
        display_time = quote_data.get('display_time', '')
        
        # Calculate image size
        width, height = self.width, self.height
        
        # Create the two images (black and red channels)
        black_image = Image.new('1', (width, height), 255)
        red_image = Image.new('1', (width, height), 255)
        
        black_draw = ImageDraw.Draw(black_image)
        red_draw = ImageDraw.Draw(red_image)
        
        # Set padding for aesthetic spacing
        padding = 40
        
        # Calculate metadata height
        meta_text = f"—{book}, {author}" if book and author else ""
        
        if meta_text:
            # Calculate optimal font size for quote first to determine relation
            quote_font_size, wrapped_quote = self.calculate_optimal_font_size(
                quote, display_time,
                width, height,
                0  # Temporarily use 0 for metadata height
            )
            
            # Calculate metadata font size - make it smaller than quote text
            # Start with a relative size to the quote (approximately 50% of quote size)
            meta_font_size = int(quote_font_size * 0.5)
            
            # Make sure we have a font in that size
            available_sizes = sorted(self.fonts['meta'].keys())
            if meta_font_size not in available_sizes:
                # Find closest available size
                smaller_sizes = [s for s in available_sizes if s <= meta_font_size]
                if smaller_sizes:
                    meta_font_size = max(smaller_sizes)
                else:
                    # If no smaller size exists, use the smallest available
                    meta_font_size = min(available_sizes)
            
            meta_font = self.fonts['meta'].get(meta_font_size)
            if not meta_font:
                meta_font = self.fonts['meta'][min(available_sizes)]
                meta_font_size = min(available_sizes)
            
            # Calculate max width for metadata
            max_meta_width = width - 2 * padding
            
            # Check if metadata fits in one line with the current font size
            meta_width = meta_font.getlength(meta_text)
            
            # If too long, reduce font size until it fits
            while meta_width > max_meta_width and meta_font_size > min(available_sizes):
                # Try smaller font size - find next smaller available size
                smaller_sizes = [s for s in available_sizes if s < meta_font_size]
                if smaller_sizes:
                    meta_font_size = max(smaller_sizes)
                    meta_font = self.fonts['meta'][meta_font_size]
                    meta_width = meta_font.getlength(meta_text)
                    logger.info(f"Reduced metadata font size to {meta_font_size}px (width: {meta_width}px / max: {max_meta_width}px)")
                else:
                    # No smaller sizes available
                    break
            
            # If still too long after trying smallest font, truncate with ellipsis
            if meta_width > max_meta_width:
                logger.info(f"Metadata text too long even at smallest font size {meta_font_size}px, truncating with ellipsis")
                ellipsis = "..."
                ellipsis_width = meta_font.getlength(ellipsis)
                
                # Try different truncation points
                for i in range(len(meta_text) - 1, 0, -1):
                    truncated = meta_text[:i] + ellipsis
                    if meta_font.getlength(truncated) <= max_meta_width:
                        meta_text = truncated
                        logger.info(f"Truncated metadata to: {meta_text}")
                        break
            
            # Metadata is now guaranteed to fit on one line
            line_height = int(meta_font_size * 1.2)  # 20% spacing
            metadata_height = line_height
            logger.info(f"Metadata height: {metadata_height}px with font size {meta_font_size}px")
        else:
            metadata_height = 0
            logger.info("No metadata to display")
        
        # Recalculate optimal font size with correct metadata height
        quote_font_size, wrapped_quote = self.calculate_optimal_font_size(
            quote, display_time, 
            width, height, 
            metadata_height
        )
        logger.info(f"Using font size {quote_font_size}px for quote")
        
        # Get fonts for the selected size
        normal_font = self.fonts['normal'][quote_font_size]
        bold_font = self.fonts['bold'][quote_font_size]
        
        # Draw the quote (with or without time highlighted)
        if display_time and display_time.lower() in quote.lower():
            # Draw quote with time highlighted
            self.draw_quote_with_highlighted_time(
                black_draw, red_draw, 
                (padding, padding), 
                wrapped_quote, display_time,
                normal_font, bold_font,
                override_line_height=int(quote_font_size * 1.2)  # Use consistent line height based on font size
            )
        else:
            # Draw the quote normally
            black_draw.multiline_text(
                (padding, padding), 
                wrapped_quote, 
                fill=0, 
                font=normal_font,
                spacing=int(quote_font_size * 1.2) - normal_font.getbbox("A")[3]  # Adjust for proper line spacing
            )
            
            # If time isn't in quote, draw it separately at the bottom
            if display_time:
                # Get a larger font for the time string (approximately 20% larger)
                larger_size = int(quote_font_size * 1.2)
                available_sizes = sorted(self.fonts['bold'].keys())
                larger_sizes = [s for s in available_sizes if s >= larger_size]
                
                if larger_sizes:
                    time_font_size = min(larger_sizes)
                    time_font = self.fonts['bold'][time_font_size]
                    logger.info(f"Using larger font size for separate time: {time_font_size}px (original: {quote_font_size}px)")
                else:
                    # If no larger size is available, use the largest available
                    time_font_size = max(available_sizes)
                    time_font = self.fonts['bold'][time_font_size]
                    logger.info(f"Using largest available font for separate time: {time_font_size}px")
                
                black_draw.text(
                    (width // 2, height - padding - metadata_height - 20), 
                    display_time, 
                    fill=0, 
                    font=time_font,
                    anchor="ms"
                )
        
        # Draw metadata at the bottom right (now as a single line)
        if meta_text:
            meta_y = height - padding - metadata_height // 2  # Centered vertically in metadata area
            black_draw.text(
                (width - padding, meta_y), 
                meta_text, 
                fill=0, 
                font=meta_font,
                anchor="rm"  # Right-middle alignment
            )
        
        # Add debug visuals if enabled
        if debug:
            self.draw_debug_info(black_draw, red_draw, metadata_height, quote_font_size, padding)
        
        return black_image, red_image
    
    def generate_and_save(self, time_str, quote_data=None):
        """Generate and save an image for a given time"""
        # Get quote for the time if not provided
        if not quote_data:
            quote_data = self.get_quote_for_time(time_str)
        
        if not quote_data:
            logger.error(f"No quote found for time {time_str}")
            return None, None
        
        # Add time_str to quote_data if not present
        if 'display_time' not in quote_data:
            quote_data['display_time'] = time_str
        
        black_image, red_image = self.create_image(quote_data)
        
        if black_image and red_image:
            # Create directory if it doesn't exist
            if not os.path.exists(self.img_dir):
                os.makedirs(self.img_dir)
            
            # Create filenames based on time
            time_parts = time_str.split(':')
            if len(time_parts) == 2:
                hour, minute = time_parts
                filename_base = f"{hour.zfill(2)}_{minute.zfill(2)}"
                black_path = os.path.join(self.img_dir, f"{filename_base}_black.bmp")
                red_path = os.path.join(self.img_dir, f"{filename_base}_red.bmp")
                
                # Save the images
                try:
                    black_image.save(black_path)
                    red_image.save(red_path)
                    logger.info(f"Saved images: {black_path}, {red_path}")
                    return black_path, red_path
                except Exception as e:
                    logger.error(f"Error saving images: {e}")
                    return None, None
            else:
                logger.error(f"Invalid time format: {time_str}")
                return None, None
        
        return None, None

def main():
    """Run a test of the image generator"""
    import datetime
    import argparse
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description='Generate test image for literary clock')
    parser.add_argument('--time', help='Time to generate image for (HH:MM format)')
    parser.add_argument('--config', default='data/config.json', help='Path to config file')
    parser.add_argument('--debug', action='store_true', help='Enable debug output with size information')
    parser.add_argument('--test-sizes', action='store_true', help='Test multiple font sizes')
    args = parser.parse_args()
    
    generator = ImageGenerator(args.config, debug=args.debug)
    
    if args.test_sizes:
        # Run a test with a specific quote and multiple font sizes
        test_font_sizes(generator, args.debug)
        return
    
    # Generate image for specified time or current time
    if args.time:
        time_str = args.time
    else:
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M")
    
    logger.info(f"Generating image for time: {time_str}")
    black_path, red_path = generator.generate_and_save(time_str)
    
    if black_path and red_path:
        logger.info(f"Images generated successfully: {black_path}, {red_path}")
    else:
        logger.error("Failed to generate images")

def test_font_sizes(generator, debug=False):
    """Test with a specific quote and different font sizes"""
    # Sample quote for testing
    test_quote = {
        "quote": "The quick brown fox jumps over the lazy dog at precisely ten o'clock in the morning. The forest was quiet, and the sun had just begun its ascent over the horizon. This longer quote will allow us to test multiple font sizes and wrapping behavior.",
        "display_time": "ten o'clock",
        "author": "Test Author",
        "book": "Font Size Test Book"
    }
    
    # Test with different font sizes - using much larger sizes
    for size in [40, 60, 80, 100, 120, 140, 160, 180]:
        logger.info(f"Testing with fixed font size: {size}px")
        
        # Create images without using optimal font calculation
        black_image = Image.new('1', (generator.width, generator.height), 255)
        red_image = Image.new('1', (generator.width, generator.height), 255)
        
        black_draw = ImageDraw.Draw(black_image)
        red_draw = ImageDraw.Draw(red_image)
        
        # Set padding
        padding = 40
        
        # Calculate metadata height
        metadata_height = 0
        metadata_text = f"—{test_quote['book']}, {test_quote['author']}"
        meta_font = generator.fonts['meta'][66]
        
        # Wrap metadata if too long
        max_meta_width = generator.width - 2 * padding
        wrapped_metadata = generator.wrap_text(metadata_text, meta_font, max_meta_width)
        metadata_lines = wrapped_metadata.split('\n')
        
        # Calculate height for metadata - scale based on test size
        meta_line_height = int(66 * 1.2)  # Use the meta font size (66) with 20% spacing
        metadata_height = len(metadata_lines) * meta_line_height
        logger.info(f"Using metadata line height: {meta_line_height}px")
        
        # Draw metadata
        meta_y = generator.height - padding - metadata_height
        for i, line in enumerate(metadata_lines):
            black_draw.text(
                (generator.width - padding, meta_y), 
                line, 
                fill=0, 
                font=meta_font,
                anchor="rt"
            )
            meta_y += meta_line_height
        
        # Get fonts for this size
        normal_font = generator.fonts['normal'].get(size, ImageFont.load_default())
        bold_font = generator.fonts['bold'].get(size, ImageFont.load_default())
        
        # Wrap text manually
        max_width = generator.width - 2 * padding
        wrapped_quote = generator.wrap_text(test_quote['quote'], normal_font, max_width)
        
        # Calculate a reasonable line height based on the test size
        # Since we can't change the actual font, we'll override the line height
        # to simulate different font sizes
        override_line_height = int(size * 1.2)  # 20% spacing
        logger.info(f"Using override line height for text: {override_line_height}px (based on font size {size}px)")
        
        # Draw quote
        generator.draw_quote_with_highlighted_time(
            black_draw, red_draw,
            (padding, padding),
            wrapped_quote, test_quote['display_time'],
            normal_font, bold_font,
            override_line_height=override_line_height
        )
        
        # Draw debug information
        generator.draw_debug_info(black_draw, red_draw, metadata_height, size, padding)
        
        # Save images
        size_str = f"{size:03d}"
        black_path = os.path.join(generator.img_dir, f"test_size_{size_str}_black.bmp")
        red_path = os.path.join(generator.img_dir, f"test_size_{size_str}_red.bmp")
        
        black_image.save(black_path)
        red_image.save(red_path)
        
        logger.info(f"Saved test images for font size {size}px: {black_path}, {red_path}")
        
    logger.info("Font size tests completed. Check the images directory for results.")

if __name__ == "__main__":
    main() 