#!/usr/bin/env python3
import os
import sys
import logging
import argparse
import threading

# Set up logging
logger = logging.getLogger(__name__)

def run_clock(config_path='data/config.json', regenerate=False):
    """Run the literary clock"""
    from litclock.clock import LiteraryClock
    
    clock = LiteraryClock(config_path)
    
    if regenerate:
        clock.regenerate_json()
    
    clock.run()

def run_web_server(host='0.0.0.0', port=8080):
    """Run the web server"""
    from litclock.web import WebInterface
    
    web_interface = WebInterface()
    web_interface.run(host=host, port=port)

def start_web_server_thread(host='0.0.0.0', port=8080):
    """Start the web server in a separate thread"""
    from litclock.web import start_web_server_thread
    
    return start_web_server_thread(host, port)

def run_all(config_path='data/config.json', regenerate=False, web_port=8080, web_host='0.0.0.0'):
    """Run both the clock and web server"""
    # Start the web server in a separate thread
    web_thread = start_web_server_thread(web_host, web_port)
    logger.info(f"Web interface started on http://{web_host}:{web_port}/")
    
    # Run the clock in the main thread
    run_clock(config_path, regenerate)

def main():
    """Main entry point for the CLI"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("litclock_runner.log"),
            logging.StreamHandler()
        ]
    )
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Literary Clock CLI')
    parser.add_argument('--web-only', action='store_true', help='Run only the web interface')
    parser.add_argument('--clock-only', action='store_true', help='Run only the clock')
    parser.add_argument('--config', default='data/config.json', help='Path to config file')
    parser.add_argument('--regenerate', action='store_true', help='Regenerate JSON from CSV')
    parser.add_argument('--web-port', type=int, default=8080, help='Web interface port')
    parser.add_argument('--web-host', default='0.0.0.0', help='Web interface host')
    
    args = parser.parse_args()
    
    try:
        # Make sure required directories exist
        os.makedirs('data', exist_ok=True)
        os.makedirs('images', exist_ok=True)
        os.makedirs('fonts', exist_ok=True)
        
        if args.web_only:
            logger.info("Starting web interface only")
            run_web_server(args.web_host, args.web_port)
        elif args.clock_only:
            logger.info("Starting clock only")
            run_clock(args.config, args.regenerate)
        else:
            # Start both services
            logger.info("Starting web interface and clock")
            run_all(args.config, args.regenerate, args.web_port, args.web_host)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 