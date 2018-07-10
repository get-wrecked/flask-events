import binascii
import codecs
import sys
import time
from collections import OrderedDict

import libhoney
from flask import request, _app_ctx_stack as stack

from . import UnitedMetric
from ._version import __version__
from .outlets import LogfmtOutlet, LibhoneyOutlet

HAS_SQLALCHEMY = False
try:
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    HAS_SQLALCHEMY = True
except ImportError:
    pass


if sys.version_info < (3, 5, 0):
    ERROR_HANDLER = 'custom-backslashreplace'

    def custom_backslashreplace(exception):
        '''Backport of backslashreplace for decoding'''
        unencodable_part = exception.object[exception.start:exception.end]
        return '\\x' + binascii.hexlify(unencodable_part).decode('ascii'), exception.end

    codecs.register_error(ERROR_HANDLER, custom_backslashreplace)
else:
    ERROR_HANDLER = 'backslashreplace'


class Events(object):
    '''
    Helper class to log canonical log lines for each request.
    '''
    # A couple of the methods here don't use self since the state during the
    # request is stored on the application context for thread safety, but are
    # kept as methods since the API is better that way.

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)


    def init_app(self, app):
        app.before_request(_before_request)
        app.after_request(_after_request)
        app.teardown_request(self._teardown_request)
        app.teardown_appcontext(self._teardown_appcontext)

        self.outlets = [LogfmtOutlet(app.name)]

        libhoney_key = app.config.get('EVENTS_HONEYCOMB_KEY')
        libhoney_dataset = app.config.get('EVENTS_HONEYCOMB_DATASET', app.name)
        if libhoney_key:
            libhoney_client = libhoney.Client(
                writekey=libhoney_key,
                dataset=libhoney_dataset,
                user_agent_addition='flask-events/%s' % __version__,
            )
            self.outlets.append(LibhoneyOutlet(libhoney_client))


    def add(self, key, value, unit=None): # pylint: disable=no-self-use
        if unit is not None:
            value = UnitedMetric(value, unit)
        add_extra(key, value)


    def _teardown_request(self, exception):
        params = get_default_params()
        for key, val in params.items():
            self.add(key, val)


    def _teardown_appcontext(self, exception):
        database_timings = get_prop('canonical_database_timings')
        if database_timings is not None:
            self.add('database_query_time', sum(database_timings), unit='seconds')
            self.add('database_executes', len(database_timings))

        canonical_start_time = get_prop('canonical_start_time')
        if canonical_start_time is None:
            # App context was pushed and popped without a request context, ignore
            return

        self.add('request_total', time.time() - canonical_start_time, unit='seconds')

        params = get_prop('canonical_log_extra', OrderedDict())

        if exception:
            params['error'] = exception.__class__.__name__
            params['error_msg'] = str(exception)

        for outlet in self.outlets:
            outlet.handle(params)


def get_default_params():
    # Don't use request.full_path since it fails to decode invalid utf-8
    # paths (as of werkzeug 0.15)
    full_path = request.path
    if request.args:
        full_path += '?' + request.query_string.decode('utf-8', ERROR_HANDLER)

    params = OrderedDict((
        ('fwd', ','.join(request.access_route)),
        ('method', request.method),
        ('path', full_path),
        ('status', get_prop('canonical_response_status', 500)),
        ('request_user_agent', request.headers.get('user-agent')),
    ))

    request_id = request.headers.get('x-request-id')
    if request_id:
        params['request_id'] = request_id

    return params


def _before_request():
    store_prop('canonical_start_time', time.time())


def _after_request(response):
    store_prop('canonical_response_status', response.status_code)
    return response


def add_extra(key, value):
    get_context().setdefault('canonical_log_extra', OrderedDict())[key] = value


def store_prop(key, value):
    get_context()[key] = value


def get_prop(key, default=None):
    return get_context().get(key, default)


def get_context():
    app_context = stack.top

    if app_context is None:
        return {}

    _context = getattr(app_context, 'flask-events', None)
    if _context is None:
        _context = {}
        setattr(app_context, 'flask-events', _context)

    return _context


if HAS_SQLALCHEMY:
    # Tracking something more accurate like actual roundtrip count is much more
    # complex since sqlalchemy doesn't give before/after signals on
    # commit/rollback, thus ignore that for now

    # Register as event handler on the database to track time spent on queries
    @event.listens_for(Engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement,
                            parameters, context, executemany):
        # pylint: disable=unused-argument,too-many-arguments
        conn.info.setdefault('flask_events_query_start_time', []).append(time.time())


    @event.listens_for(Engine, "after_cursor_execute")
    def receive_after_cursor_execute(conn, cursor, statement,
                            parameters, context, executemany):
        # pylint: disable=unused-argument,too-many-arguments,too-many-locals
        total = time.time() - conn.info['flask_events_query_start_time'].pop(-1)
        get_context().setdefault('canonical_database_timings', []).append(total)
