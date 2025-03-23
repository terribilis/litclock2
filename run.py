#!/usr/bin/env python3
import os
import sys
import time
import logging
import argparse
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("litclock_runner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("litclock_runner")

# Import web interface
try:
    from web_interface import start_web_server_thread
except ImportError as e:
    logger.error(f"Error importing web_interface: {e}")
    sys.exit(1)

def start_clock():
    """Start the literary clock main process"""
    try:
        import litclock
        litclock.main()
    except Exception as e:
        logger.error(f"Error starting clock: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Run Literary Clock and Web Interface')
    parser.add_argument('--web-port', type=int, default=8080, help='Web interface port')
    parser.add_argument('--web-only', action='store_true', help='Run only the web interface')
    parser.add_argument('--clock-only', action='store_true', help='Run only the clock')
    args = parser.parse_args()
    
    try:
        if args.web_only:
            logger.info("Starting web interface only")
            from web_interface import run_web_server
            run_web_server(port=args.web_port)
        elif args.clock_only:
            logger.info("Starting clock only")
            start_clock()
        else:
            # Start both services
            logger.info("Starting web interface and clock")
            
            # Start web server in a separate thread
            web_thread = start_web_server_thread(port=args.web_port)
            logger.info(f"Web interface started on port {args.web_port}")
            
            # Start the clock in the main thread
            start_clock()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 