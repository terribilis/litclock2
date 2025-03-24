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

def cleanup_gpio():
    """Clean up any in-use GPIO pins to avoid resource conflicts"""
    try:
        # Try to import and use gpiozero's cleanup function
        import gpiozero
        gpiozero.Device.close_all()
        logger.info("Successfully cleaned up GPIO resources")
        import time
        time.sleep(0.5)  # Give a little time for cleanup
        return True
    except ImportError:
        # On systems without GPIO hardware (like Mac/Windows), we just pretend it worked
        if sys.platform in ('darwin', 'win32'):
            logger.info("Running on non-Raspberry Pi system, GPIO cleanup not needed")
            return True
        logger.warning("gpiozero module not available for GPIO cleanup")
        return False
    except Exception as e:
        logger.error(f"Error during GPIO cleanup: {e}")
        return False

def test_display():
    """Run a test on the e-paper display"""
    # First clean up any GPIO resources to avoid conflicts
    cleanup_gpio()
    
    # Ensure compatibility setup is done
    try:
        from litclock.epd.compatibility import ensure_compatibility
        ensure_compatibility()
    except Exception as e:
        logger.warning(f"Compatibility setup failed: {e}, proceeding anyway")
    
    # Now run the actual test
    from litclock.epd.test_display import test_display as run_test
    
    logger.info("Running e-paper display test...")
    try:
        success = run_test()
        if success:
            logger.info("Display test completed successfully")
        else:
            logger.error("Display test failed or was interrupted")
            sys.exit(1)
    finally:
        # Always clean up GPIO at the end
        cleanup_gpio()

def run_all(config_path='data/config.json', regenerate=False, host='0.0.0.0', port=8080):
    """Run both the clock and web interface"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("litclock_runner.log"),
            logging.StreamHandler()
        ]
    )
    
    logger.info("Starting Literary Clock with Web Interface")
    
    # Start web server in a thread
    web_thread = start_web_server_thread(host, port)
    logger.info(f"Web interface started at http://{host}:{port}/")
    
    try:
        # Run the clock in the main thread
        run_clock(config_path, regenerate)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.exception(f"Error running Literary Clock: {e}")
    finally:
        logger.info("Shutting down...")
        sys.exit(0)

def main():
    """Main function to parse arguments and run the appropriate command"""
    # Create argument parser
    parser = argparse.ArgumentParser(description='Literary Clock with e-Paper Display')
    
    # Add arguments
    parser.add_argument('--web-only', action='store_true', help='Run only the web interface')
    parser.add_argument('--clock-only', action='store_true', help='Run only the clock')
    parser.add_argument('--test', action='store_true', help='Run a test on the e-paper display')
    parser.add_argument('--cleanup-gpio', action='store_true', help='Clean up GPIO resources and exit')
    parser.add_argument('--config', default='data/config.json', help='Path to config file')
    parser.add_argument('--regenerate', action='store_true', help='Regenerate quotes JSON database')
    parser.add_argument('--web-port', type=int, default=8080, help='Web interface port')
    parser.add_argument('--web-host', default='0.0.0.0', help='Web interface host')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("litclock_runner.log"),
            logging.StreamHandler()
        ]
    )
    
    # Ensure data directory exists
    data_dir = os.path.dirname(args.config)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Run the appropriate command
    try:
        if args.cleanup_gpio:
            # Just clean up GPIO and exit
            if cleanup_gpio():
                logger.info("GPIO cleanup completed successfully")
            else:
                logger.error("GPIO cleanup failed")
                return 1
            return 0
        elif args.test:
            # Run display test
            test_display()
        elif args.web_only:
            # Run only the web interface
            logger.info(f"Starting web interface at http://{args.web_host}:{args.web_port}/")
            run_web_server(args.web_host, args.web_port)
        elif args.clock_only:
            # Run only the clock
            logger.info("Starting literary clock")
            run_clock(args.config, args.regenerate)
        else:
            # Run both
            run_all(args.config, args.regenerate, args.web_host, args.web_port)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.exception(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 