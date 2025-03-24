# Literary Clock with E-Paper Display

A Raspberry Pi Zero 2 based clock that displays literary quotes matching the current time on a 13.3-inch e-paper HAT (B) device.

## Features

- Displays literary quotes that mention the current time
- Web-based settings interface for configuration
- SFW/NSFW content filtering
- Customizable update interval, font size, and display options
- CSV quote database with easy import/update

## Hardware Requirements

- Raspberry Pi Zero 2
- 13.3-inch e-paper HAT (B)
- MicroSD card
- Power supply for Raspberry Pi
- Optional: case for the display and Raspberry Pi

## Software Setup

### 1. Operating System Installation

1. Install Raspberry Pi OS Lite on your microSD card using the Raspberry Pi Imager
2. Enable SSH during setup for headless operation
3. Configure Wi-Fi credentials

### 2. Install Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-venv python3-full python3-pil git

# Clone the repository
git clone https://github.com/yourusername/litclock.git
cd litclock

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the package in development mode
pip install -e .
```

### 3. Setup Required Directories

```bash
# Create required directories
mkdir -p images fonts data

# Download some open-source fonts (optional)
wget -P fonts/ https://github.com/google/fonts/raw/main/apache/opensans/OpenSans-Regular.ttf
wget -P fonts/ https://github.com/google/fonts/raw/main/apache/opensans/OpenSans-Bold.ttf
wget -P fonts/ https://github.com/google/fonts/raw/main/apache/opensans/OpenSans-Italic.ttf
```

### 4. Test the E-Paper Display (Optional)

You can test if your e-paper display is working correctly:

```bash
# Activate the virtual environment (if not already active)
source venv/bin/activate

# Run the display test
python -m litclock.cli --test
```

This will display various patterns, text, and shapes on the e-paper display to verify everything is working correctly.

### 5. Install as a Service

```bash
# Copy service files to systemd
sudo cp systemd/litclock.service /etc/systemd/system/
sudo cp systemd/webinterface.service /etc/systemd/system/
sudo cp systemd/litclock-all.service /etc/systemd/system/

# Update file paths in service files if needed
sudo nano /etc/systemd/system/litclock.service
sudo nano /etc/systemd/system/webinterface.service
sudo nano /etc/systemd/system/litclock-all.service

# Enable and start services (choose one)
sudo systemctl daemon-reload

# Option 1: Run both the clock and web interface together
sudo systemctl enable litclock-all.service
sudo systemctl start litclock-all.service

# Option 2: Run the clock and web interface separately
sudo systemctl enable litclock.service
sudo systemctl enable webinterface.service
sudo systemctl start litclock.service
sudo systemctl start webinterface.service
```

### 6. Manually Running the Clock

If you prefer to run the clock manually rather than as a service:

```bash
# Activate the virtual environment
source venv/bin/activate

# Run both the clock and web interface
python -m litclock.cli

# Run only the web interface
python -m litclock.cli --web-only

# Run only the clock
python -m litclock.cli --clock-only
```

## Web Interface

The web interface is accessible at `http://<raspberry-pi-ip>:8080/` and allows you to:

- Change the update interval
- Set the font size
- Show/hide book information and author
- Filter content (SFW/NSFW/All)
- Upload a new quotes CSV file
- Regenerate the JSON database from CSV

## CSV Format

The quotes CSV file should follow this format:
```
HH:MM|Display Time|Quote|Book|Author|Rating
```

Example:
```
13:35|1:35 P.M.|Fletcher checked his watch again. It was 1:35 P.M. He sighed and asked the receptionist if he could use the washroom.|Sons of Fortune|Jeffrey Archer|sfw
```

## Configuration

The `data/config.json` file contains the following settings:

```json
{
    "update_interval": 600,
    "font_size": 40,
    "show_book_info": true,
    "show_author": true,
    "content_filter": "all",
    "display_brightness": 100
}
```

- `update_interval`: Time in seconds between display updates (default: 600)
- `font_size`: Base font size for quotes (default: 40)
- `show_book_info`: Whether to display the book title (default: true)
- `show_author`: Whether to display the author name (default: true)
- `content_filter`: Content filter setting ("all", "sfw", or "nsfw")
- `display_brightness`: Display brightness percentage (0-100)

## Package Structure

The project is organized as a Python package:

```
litclock/
├── litclock/           # Main package
│   ├── __init__.py
│   ├── cli.py          # Command-line interface
│   ├── clock.py        # Clock functionality
│   ├── web.py          # Web interface
│   ├── epd/            # E-paper display drivers
│   │   ├── __init__.py
│   │   ├── epdconfig.py
│   │   └── epd13in3b.py
│   ├── utils/          # Utility functions
│   │   ├── __init__.py
│   │   ├── csv_converter.py
│   │   └── image_generator.py
│   ├── templates/      # Flask templates
│   └── static/         # Static files for web UI
├── data/               # Data files
│   ├── config.json
│   ├── quotes.json
│   └── litclock_annotated.csv
├── fonts/              # Font files
├── images/             # Generated images
├── systemd/            # Systemd service files
└── setup.py            # Package setup file
```

## Troubleshooting

- **Display Issues**: Check the connections between the Raspberry Pi and the e-paper display.
- **Web Interface Not Loading**: Ensure the web interface service is running and check firewall settings.
- **Quote Not Updating**: Check the log files for errors (`litclock_runner.log` and `web_interface.log`).
- **Import Errors**: Make sure you're running from the virtual environment with all dependencies installed.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on Waveshare e-paper display driver
- Inspired by the Literary Clock concept from the Instructables community
- Quotes data adapted from various literary clock projects