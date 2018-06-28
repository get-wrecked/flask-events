#!/bin/sh

set -e

./venv/bin/pylint --rcfile .pylintrc \
    flask_events \
    tests/*.py
