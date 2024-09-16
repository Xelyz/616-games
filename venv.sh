#!/bin/bash

# Try finding Python 3.12 in common locations
PYTHON=${PYTHON:-$(command -v /usr/local/bin/python3.12 || command -v /usr/bin/python3.12)}

# Exit if Python 3.12 is not found
[ -z "$PYTHON" ] && echo "Python 3.12 not found." && exit 1

# Create a virtual environment if it doesn't exist
[ ! -d .venv ] && $PYTHON -m venv .venv

# Exit if the virtual environment was not successfully created
[ ! -d .venv ] && echo "Failed to create virtual environment." && exit 1

# Activate the virtual environment if it's not already active
[ -z "$VIRTUAL_ENV" ] && source .venv/bin/activate

# Upgrade pip, setuptools, and wheel, and install required packages
pip install --upgrade pip setuptools wheel discord.py python-dotenv