#!/usr/bin/env python3
import csv
import json
import os
import argparse
import logging

logger = logging.getLogger(__name__)

def convert_csv_to_json(csv_file, json_file):
    """
    Convert a CSV file with quote data to JSON format
    CSV format: HH:MM|H:MM A.M.|Quote|Book|Author|Rating
    """
    logger.info(f"Converting {csv_file} to {json_file}")
    
    quotes_dict = {}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f, delimiter='|')
            for row in csv_reader:
                if len(row) < 6:
                    logger.warning(f"Skipping invalid row: {row}")
                    continue
                
                time_key = row[0]  # HH:MM format
                display_time = row[1]
                quote = row[2]
                book = row[3]
                author = row[4]
                rating = row[5].lower()
                
                # If this time already exists, append to an array
                if time_key in quotes_dict:
                    # If it's not already a list, convert it to one
                    if not isinstance(quotes_dict[time_key], list):
                        quotes_dict[time_key] = [quotes_dict[time_key]]
                    
                    # Add the new quote
                    quotes_dict[time_key].append({
                        "display_time": display_time,
                        "quote": quote,
                        "book": book,
                        "author": author,
                        "rating": rating
                    })
                else:
                    quotes_dict[time_key] = {
                        "display_time": display_time,
                        "quote": quote,
                        "book": book,
                        "author": author,
                        "rating": rating
                    }
        
        # Write the JSON file
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(quotes_dict, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Successfully converted to {json_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error converting CSV to JSON: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Convert quote CSV to JSON format')
    parser.add_argument('--csv', default='data/litclock_annotated.csv', help='Path to the CSV file')
    parser.add_argument('--json', default='data/quotes.json', help='Path to output JSON file')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    convert_csv_to_json(args.csv, args.json)
    
if __name__ == "__main__":
    main() 