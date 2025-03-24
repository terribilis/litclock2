# Literary Clock Package

This is the main package for the Literary Clock project.

## Modules

- `cli.py`: Command-line interface for running both the clock and web interface
- `clock.py`: Core functionality for the literary clock display
- `web.py`: Web interface for configuring the clock
- `epd/`: E-paper display drivers
- `utils/`: Utility functions for image generation and CSV conversion

## Usage

Run the clock and web interface:
```bash
python -m litclock
```

Run just the clock:
```bash
python -m litclock --clock-only
```

Run just the web interface:
```bash
python -m litclock --web-only
```

Test the e-paper display:
```bash
python -m litclock --test
```

Additional options:
```bash
python -m litclock --help
``` 