from setuptools import setup, find_packages

setup(
    name="litclock",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "RPi.GPIO",
        "spidev",
        "pillow",
        "flask",
        "werkzeug",
        "gpiozero"
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "litclock=litclock.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="Literary Clock for e-Paper Display",
    keywords="raspberry pi, e-paper, clock, literature",
    include_package_data=True,
    package_data={
        "litclock": ["templates/*", "static/*", "static/css/*", "static/js/*"]
    },
) 