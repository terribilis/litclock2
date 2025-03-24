# Utility Functions

This package contains utility functions for the Literary Clock project.

## Files

- `csv_converter.py`: Functions for converting CSV data to JSON and managing the quotes database
- `image_generator.py`: Functions for generating images to display on the e-paper screen

## Usage

### CSV Converter

```python
from litclock.utils.csv_converter import convert_csv_to_json, get_quote_for_time

# Convert CSV file to JSON
convert_csv_to_json('data/litclock_annotated.csv', 'data/quotes.json')

# Get a quote for a specific time
quote = get_quote_for_time('13:45', filter_mode='sfw')
```

### Image Generator

```python
from litclock.utils.image_generator import create_quote_image

# Create an image with the quote
image = create_quote_image(
    quote_text="The time was exactly a quarter to two.",
    book_title="Great Expectations",
    author="Charles Dickens",
    display_time="1:45",
    font_size=40,
    show_book_info=True,
    show_author=True
)
``` 