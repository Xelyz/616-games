#!/bin/bash

[ -z "$PYTHON" ] && [ -f /var/packages/python312/target/bin/python3 ] && PYTHON=/var/packages/python312/target/bin/python3
[ -z "$PYTHON" ] && [ -f /usr/local/bin/python3.12 ] && PYTHON=/usr/local/bin/python3.12
[ -z "$PYTHON" ] && exit

[ ! -d .venv ] && $PYTHON -m venv .venv
[ -z "$VIRTUAL_ENV" ] && source .venv/bin/activate

pip install --upgrade pip setuptools wheel discord.py python-dotenv
