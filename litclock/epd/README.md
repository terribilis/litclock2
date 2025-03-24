# E-Paper Display Drivers

This package contains the necessary drivers for the 13.3-inch e-paper HAT (B) display.

## Files

- `epd13in3b.py`: Driver for the 13.3-inch e-paper display with black and red colors
- `epdconfig.py`: Configuration and GPIO setup for e-paper display
- `test_display.py`: Test script to verify the e-paper display is working correctly

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

## Testing the Display

You can test if your e-paper display is working correctly using the included test script:

```bash
# After installing the package (pip install -e .)
python -m litclock.epd.test_display
```

This will run a comprehensive test displaying various patterns, text, and shapes on the e-paper display.

## Credits

Based on the Waveshare e-paper display driver library. 