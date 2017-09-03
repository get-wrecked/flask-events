#!/bin/sh

./venv/bin/py.test \
    --cov flask_canonical \
    --cov-report html:coverage \
    tests/
firefox coverage/index.html
