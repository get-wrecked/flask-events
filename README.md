Flask-Canonical
===============

Flask middleware to help log with [canonical logging](https://brandur.org/canonical-log-lines).


Installation
------------

    $ pip install flask-canonical


Using it
--------

General usage requires nothing more than calling `init_app` or initiating the logger with the app directly:

```python
from flask_canonical import CanonicalLogger
from flask import Flask

app = Flask(__name__)
canonical_logger = CanonicalLogger(app)

@app.route('/')
def main():
    return 'Hello, world!'
```

It logs to a logger called `<app-name>.canonical`, configure your logging to forward this to syslog or a log file or stdout however you like.
