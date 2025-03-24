#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import time
import re

def test_times():
    """Test various times to verify font scaling"""
    # Test a variety of times
    test_times = [
        "00:05", "01:15", "05:45", "08:30", "12:00", 
        "12:34", "15:15", "18:00", "20:45", "23:55"
    ]
    
    results = []
    
    for test_time in test_times:
        print(f"\nTesting time: {test_time}")
        command = f"python -m litclock.utils.image_generator --time \"{test_time}\" --debug"
        
        # Run the command and capture the output
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Print the exit code to ensure the command executed successfully
        print(f"Exit code: {result.returncode}")
        
        # Process the output to get the selected font size
        output_lines = result.stdout.split('\n')
        
        # Look for the line that contains the selected font size
        font_size = None
        space_usage = None
        
        for line in output_lines:
            if "Selected best font size:" in line:
                # Extract the font size and space usage
                font_size_match = re.search(r'Selected best font size: (\d+)px', line)
                space_usage_match = re.search(r'space usage: ([\d.]+)%', line)
                
                if font_size_match and space_usage_match:
                    font_size = font_size_match.group(1)
                    space_usage = space_usage_match.group(1)
                    print(f"Found font size: {font_size}px, space usage: {space_usage}%")
                    break
        
        # Check if images were saved
        saved_images = []
        for line in output_lines:
            if "Saved images:" in line:
                # Extract the image paths
                image_paths = line.split("Saved images:")[1].strip()
                saved_images = [img.strip() for img in image_paths.split(',')]
                print(f"Saved images: {', '.join(saved_images)}")
                break
        
        # Add to results if font size was found
        if font_size and space_usage:
            results.append({
                "time": test_time,
                "font_size": int(font_size),
                "space_usage": float(space_usage),
                "images": saved_images
            })
        else:
            print(f"WARNING: Could not extract font size for time {test_time}")
            
        # Small pause between tests
        time.sleep(1)
    
    return results

def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*80)
    print("TESTING FONT SCALING FOR VARIOUS TIMES")
    print("="*80)
    
    # Make sure the images directory exists
    if not os.path.exists("images"):
        os.makedirs("images")
        
    # Run the tests
    results = test_times()
    
    # Print a summary of font sizes
    if results:
        print("\n" + "="*80)
        print("FONT SIZE SUMMARY (sorted by size)")
        print("="*80)
        # Sort by font size, largest to smallest
        sorted_results = sorted(results, key=lambda x: x["font_size"], reverse=True)
        for result in sorted_results:
            print(f"Time {result['time']}: Font size {result['font_size']}px, Space usage {result['space_usage']}%")
    else:
        print("\nNo font size results collected. Check debug output for errors.")
    
    # List the last 20 image files generated
    print("\n" + "="*80)
    print("LAST 20 IMAGE FILES")
    print("="*80)
    
    result = subprocess.run("ls -l images/*.bmp | tail -20", shell=True, capture_output=True, text=True)
    print(result.stdout)
    
    print("\nTesting complete!")

if __name__ == "__main__":
    run_all_tests() 