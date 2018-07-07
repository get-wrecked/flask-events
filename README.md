Flask-Events
===============

Flask middleware to help log with structured event logging to multiple outlets (logfmt, honeycomb, etc).

This project was forked from [Flask-Canonical](https://github.com/megacool/flask-canonical/) to
enable multiple outlets. If you only need a single logfmt outlet, flask-canonical is probably all
you need.


Installation
------------

    $ pip install flask-events


Using it
--------

General usage with only a logfmt outlet requires nothing more than calling `init_app` or initiating
the logger with the app directly:

```python
from flask import Flask
from flask_events import Events

app = Flask(__name__)
events = Events(app)

@app.route('/')
def main():
    events.add('key', 'value')
    return 'Hello, world!'
```

It logs to a logger called `<app-name>.canonical`, configure your logging to forward this to syslog or a log file or stdout however you like:

    fwd=127.0.0.1 tag=main method=GET path=/ status=200 request_user_agent=curl/7.38.0 key=value measure#timing_total=0.001s

To also include a Honeycomb outlet, set `EVENTS_HONEYCOMB_KEY` in the app config. It will by default write to a dataset named after the app, or you can set a custom dataset name by setting `EVENTS_HONEYCOMB_DATASET`.

If you're using SQLAlchemy query timing from the database is tracked automatically.

There is a sample app in `sample_app.py` you can inspect and fire up if you want to play around and learn how it works.


Development
-----------

    $ ./configure
    $ ./test
