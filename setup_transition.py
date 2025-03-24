#!/usr/bin/env python3
"""
Transition script to help set up the new package structure
and create necessary directories if they don't exist.
"""

import os
import shutil
import json
import sys

def create_directory(dir_path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_path}")
    else:
        print(f"Directory already exists: {dir_path}")

def ensure_directories():
    """Ensure all required directories exist."""
    directories = ['data', 'images', 'fonts']
    for directory in directories:
        create_directory(directory)

def setup_data_directory():
    """Set up the data directory with necessary files."""
    # Create default config if it doesn't exist
    if not os.path.exists('data/config.json'):
        default_config = {
            "update_interval": 600,
            "font_size": 40,
            "show_book_info": True,
            "show_author": True,
            "content_filter": "all",
            "display_brightness": 100
        }
        with open('data/config.json', 'w') as f:
            json.dump(default_config, f, indent=4)
        print("Created default config.json")

def main():
    """Main function to set up transition."""
    print("Setting up Literary Clock transition...")
    
    # Ensure necessary directories exist
    ensure_directories()
    
    # Set up data directory
    setup_data_directory()
    
    # Completion message
    print("\nTransition setup complete!")
    print("\nTo complete the transition, run:")
    print("  pip install -e .")
    print("\nThen you can run the literary clock with:")
    print("  python -m litclock")
    print("  python -m litclock --web-only")
    print("  python -m litclock --clock-only")

if __name__ == "__main__":
    main() 