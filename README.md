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

It logs to a logger called `<app-name>.canonical`, configure your logging to forward this to syslog or a log file or stdout however you like:

    fwd=127.0.0.1 tag=main method=GET path=/ status=200 request_user_agent=curl/7.38.0 measure#timing_total=0.001s

Timing data is logged in a format similar to [l2met](https://github.com/ryandotsmith/l2met), `measure#db.total=0.002s`. If you're using SQLAlchemy timing from the database is tracked automatically.

There is a sample app in `sample_app.py` you can inspect and fire up if you want to play around with the logger.


Development
-----------

    $ ./configure
    $ ./test
