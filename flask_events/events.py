import binascii
import codecs
import sys
import time
from collections import OrderedDict

from flask import request, _app_ctx_stack as stack

from . import UnitedMetric
from .outlets import LogfmtOutlet

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
        self.app = app

        app.before_request(_before_request)
        app.after_request(_after_request)
        app.teardown_request(self._teardown_request)

        self.outlets = [LogfmtOutlet(app.name)]


    def add(self, key, value, unit=None): # pylint: disable=no-self-use
        if unit is not None:
            value = UnitedMetric(value, unit)
        add_extra(key, value)


    def _teardown_request(self, exception):
        params = get_default_params()

        timing_database = get_prop('canonical_timing_database')
        if timing_database is not None:
            self.add('database_total', timing_database, unit='seconds')

        self.add('request_total', time.time() - get_prop('canonical_start_time'), unit='seconds')

        for key, value in get_prop('canonical_log_extra', ()):
            params[key] = value

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
    get_context().setdefault('canonical_log_extra', []).append((key, value))


def store_prop(key, value):
    get_context()[key] = value


def get_prop(key, default=None):
    return get_context().get(key, default)


def get_context():
    app_context = stack.top

    if not app_context:
        return {}

    _context = getattr(app_context, 'canonical', None)
    if not _context:
        _context = {}
        setattr(app_context, 'canonical', _context)

    return _context


if HAS_SQLALCHEMY:
    # Register as event handler on the database to track time spent
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement,
                            parameters, context, executemany):
        # pylint: disable=unused-argument,too-many-arguments
        conn.info.setdefault('query_start_time', []).append(time.time())


    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement,
                            parameters, context, executemany):
        # pylint: disable=unused-argument,too-many-arguments,too-many-locals
        total = time.time() - conn.info['query_start_time'].pop(-1)
        timing_database = get_prop('canonical_timing_database', 0)
        store_prop('canonical_timing_database', timing_database + total)
