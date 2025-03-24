# E-Paper Display Drivers

This package contains the necessary drivers for the 13.3-inch e-paper HAT (B) display.

## Files

- `epd13in3b.py`: Driver for the 13.3-inch e-paper display with black and red colors
- `epdconfig.py`: Configuration and GPIO setup for e-paper display

## Usage

These drivers are imported and used by the main clock functionality:

```python
from litclock.epd import epd13in3b

# Initialize the display
epd = epd13in3b.EPD()
epd.init()

# Display an image
epd.display(black_image, red_image)

# Sleep the display when not in use
epd.sleep()
```

## Credits

Based on the Waveshare e-paper display driver library. 