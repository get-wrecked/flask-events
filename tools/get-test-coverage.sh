#!/bin/sh

./venv/bin/py.test \
    --cov flask_events \
    --cov-report html:coverage \
    tests/
firefox coverage/index.html
