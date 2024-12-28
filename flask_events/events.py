import binascii
import functools
import inspect
import logging
import os
import sys
import time

from collections import OrderedDict

import libhoney
from flask import current_app, request, g
from werkzeug.routing import RequestRedirect
from werkzeug.exceptions import MethodNotAllowed, NotFound

from . import UnitedMetric
from ._version import __version__
from .outlets import LogfmtOutlet, LibhoneyOutlet
from .anonymizer import Anonymizer

HAS_SQLALCHEMY = False
try:
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    HAS_SQLALCHEMY = True
except ImportError:
    pass



class Events:
    '''
    Helper class to generate structured log data for each request.
    '''
    # A couple of the methods here don't use self since the state during the
    # request is stored on the application context for thread safety, but are
    # kept as methods since the API is better that way.

    def __init__(self, app=None):
        self.outlets = []

        if app is not None:
            self.init_app(app)

        self.add_all_data = get_default_all_data()
        self.autoadd_celery_args = True


    def init_app(self, app):
        self._init(app)

        app.before_request(_before_request)
        app.after_request(_after_request)
        app.teardown_request(self._teardown_request)
        app.teardown_appcontext(self._teardown_appcontext)


    def init_celery_app(self, app):
        self._init(app)

        self.autoadd_celery_args = app.config.get('EVENTS_AUTOADD_CELERY_ARGS', True)

        from celery import signals # pylint: disable=import-outside-toplevel

        @signals.task_prerun.connect(weak=False)
        def before_task(task=None, args=None, kwargs=None, **kw): # pylint: disable=unused-argument
            app.app_context().push()
            store_prop('task_start_time', time.time())
            self.add('task', task.name)

            if not self.autoadd_celery_args:
                return

            self.add_function_arguments(task.run, args, kwargs)


        @signals.task_postrun.connect(weak=False)
        def after_task(retval=None, task_id=None, state=None, **kw): # pylint: disable=unused-argument
            task_start_time = get_prop('task_start_time')
            self.add('state', state)
            self.add('retval', retval)
            self.add('task_total', time.time() - task_start_time, unit='seconds')

            params = self.add_all_data.copy()

            # Add the task_id last to try to keep the generally most relevant data first
            self.add('task_id', task_id)

            request_extras = get_prop('request_extras')
            if request_extras is not None:
                params.update(request_extras)

            for outlet in self.outlets:
                outlet.handle(params)

            app.app_context().pop()


    def _init(self, app):
        self.outlets.clear() # In case of multiple init
        self.outlets.append(LogfmtOutlet(app.name))

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


    def add_all(self, key, value, unit=None):
        if unit is not None:
            value = UnitedMetric(value, unit)
        self.add_all_data[key] = value


    def add_function_arguments(self, func, args, kwargs):
        if args:
            signature = inspect.signature(func)
            named_args = []
            varargs_name = 'args'

            for param_name, param in signature.parameters.items():
                if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
                    named_args.append(param_name)
                elif param.kind == param.VAR_POSITIONAL:
                    varargs_name = param_name
                else:
                    break

            for parameter, value in zip(named_args, args):
                self.add(parameter, value)

            for index, vararg in enumerate(args[len(named_args):]):
                self.add('%s_%d' % (varargs_name, index), vararg)

        if kwargs:
            for key, val in kwargs.items():
                self.add(key, val)


    def instrument(self):
        def wrapper(func):
            @functools.wraps(func)
            def instrumented_func(*args, **kwargs):
                start_time = time.time()
                self.add('func_name', func.__name__)
                self.add_function_arguments(func, args, kwargs)

                try:
                    func(*args, **kwargs)
                except Exception as exc: # pylint: disable=broad-except
                    self.add('error', exc.__class__.__name__)
                    self.add('error_msg', str(exc))
                finally:
                    self.add('duration', time.time() - start_time, unit='seconds')

                    params = self.add_all_data.copy()

                    request_extras = get_prop('request_extras')
                    if request_extras is not None:
                        params.update(request_extras)

                    for outlet in self.outlets:
                        outlet.handle(params)

            return instrumented_func
        return wrapper


    def _teardown_request(self, exception): # pylint: disable=unused-argument
        params = get_default_params()
        for key, val in params.items():
            self.add(key, val)


    def _teardown_appcontext(self, exception):
        database_timings = get_prop('database_timings')
        if database_timings is not None:
            self.add('database_query_time', sum(database_timings), unit='seconds')
            self.add('database_executes', len(database_timings))

        request_start_time = get_prop('request_start_time')
        if request_start_time is None:
            # App context was pushed and popped without a request context, ignore
            return

        self.add('request_total', time.time() - request_start_time, unit='seconds')

        params = self.add_all_data.copy()
        request_extras = get_prop('request_extras')
        if request_extras is not None:
            params.update(request_extras)

        if exception:
            params['error'] = exception.__class__.__name__
            params['error_msg'] = str(exception)

        for outlet in self.outlets:
            outlet.handle(params)


def get_default_all_data():
    all_data = OrderedDict()

    heroku_release_version = os.environ.get('HEROKU_RELEASE_VERSION')
    if heroku_release_version:
        all_data['release_version'] = heroku_release_version
    heroku_slug_commit = os.environ.get('HEROKU_SLUG_COMMIT')
    if heroku_slug_commit:
        all_data['slug_commit'] = heroku_slug_commit

    return all_data


def get_default_params():
    full_path = request.full_path.rstrip('?')
    params = OrderedDict((
        ('fwd', ','.join(get_access_route())),
        ('method', request.method),
        ('path', full_path),
        ('status', get_prop('response_status', 500)),
        ('request_user_agent', request.headers.get('user-agent')),
    ))

    view_function = get_view_function(current_app, request.path, request.method)
    if view_function:
        params['handler'] = '%s.%s' % (view_function.__module__, view_function.__qualname__)

    request_id = request.headers.get('x-request-id')
    if request_id:
        params['request_id'] = request_id

    return params


def get_access_route():
    access_route = request.access_route
    anonymizer = get_anonymizer()
    if not anonymizer or not access_route:
        return access_route

    first_address = access_route[0]
    return [anonymizer.anonymize(first_address)] + access_route[1:]


def get_view_function(app, url, method):
    """Match a url and return the view and arguments
    it will be called with, or None if there is no view.
    Creds: http://stackoverflow.com/a/38488506
    """
    # pylint: disable=too-many-return-statements

    adapter = app.create_url_adapter(request)

    try:
        match = adapter.match(url, method=method)
    except RequestRedirect as ex:
        # recursively match redirects
        return get_view_function(app, ex.new_url, method)
    except (MethodNotAllowed, NotFound):
        # no match
        return None

    try:
        return app.view_functions[match[0]]
    except KeyError:
        # no view is associated with the endpoint
        return None


def get_anonymizer():
    anonymizer = getattr(g, 'flask_events_anonymizer', None)
    if anonymizer:
        return anonymizer

    anonymizer_config = current_app.config.get('EVENTS_ANONYMIZE_IPS', False)
    if not anonymizer_config:
        return None

    if anonymizer_config is True:
        anonymizer = Anonymizer()
    else:
        anonymizer = Anonymizer(**anonymizer_config)

    g.flask_events_anonymizer = anonymizer

    return anonymizer


def _before_request():
    store_prop('request_start_time', time.time())


def _after_request(response):
    store_prop('response_status', response.status_code)
    return response


def add_extra(key, value):
    get_context().setdefault('request_extras', OrderedDict())[key] = value


def store_prop(key, value):
    get_context()[key] = value


def get_prop(key, default=None):
    return get_context().get(key, default)


def get_context():
    context = getattr(g, 'flask_events', None)
    if context is None:
        context = {}
        setattr(g, 'flask_events', context)

    return context


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
        get_context().setdefault('database_timings', []).append(total)
