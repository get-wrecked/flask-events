import os
import time

from psycopg2 import extensions as _ext
from psycopg2.extensions import cursor as _cursor
from psycopg2.extensions import connection as _connection
from flask_sqlalchemy import SQLAlchemy

from flask_events.events import store_database_timing


class MetricSQLAlchemy(SQLAlchemy):
    def apply_pool_defaults(self, app, options):
        super(MetricSQLAlchemy, self).apply_pool_defaults(app, options)
        connect_args = options.get('connect_args')
        if connect_args is None:
            connect_args = {}
            options['connect_args'] = connect_args
        connect_args.setdefault('connection_factory', LoggingConnection)


class LoggingConnection(_connection):
    def cursor(self, *args, **kwargs):
        kwargs.setdefault('cursor_factory', LoggingCursor)
        return super(LoggingConnection, self).cursor(*args, **kwargs)


    def commit(self, *args, **kwargs):
        start_time = time.time()
        ret = super(LoggingConnection, self).commit(*args, **kwargs)
        store_database_timing(time.time() - start_time)
        return ret


    def rollback(self, *args, **kwargs):
        start_time = time.time()
        ret = super(LoggingConnection, self).commit(*args, **kwargs)
        store_database_timing(time.time() - start_time)
        return ret


class LoggingCursor(_cursor):
    """A cursor that logs queries using its connection logging facilities."""

    def execute(self, query, vars=None):
        start_time = time.time()
        try:
            return super(LoggingCursor, self).execute(query, vars)
        finally:
            store_database_timing(time.time() - start_time)


    def callproc(self, procname, vars=None):
        start_time = time.time()
        try:
            return super(LoggingCursor, self).callproc(procname, vars)
        finally:
            store_database_timing(time.time() - start_time)


# Dump of an alternate approach instead of overriding the connection purely using sqlalchemy signals:
# (the problem with this is that begin/commit/rollback can't be timed and thus will only contribute to the roundtrip counter but not the time spent)
# if HAS_SQLALCHEMY:
#     Register as event handler on the database to track time spent
#     @event.listens_for(Engine, "before_cursor_execute")
#     def receive_before_cursor_execute(conn, cursor, statement,
#                             parameters, context, executemany):
#         # pylint: disable=unused-argument,too-many-arguments
#         print('starting statement %s' % statement)
#         conn.info.setdefault('flask_events_query_start_time', []).append(time.time())


#     @event.listens_for(Engine, "after_cursor_execute")
#     def receive_after_cursor_execute(conn, cursor, statement,
#                             parameters, context, executemany):
#         # pylint: disable=unused-argument,too-many-arguments,too-many-locals
#         total = time.time() - conn.info['flask_events_query_start_time'].pop(-1)
#         store_database_timing(total)
#         print('finished statement %s' % statement)


#     @event.listens_for(Engine, 'begin')
#     def receive_begin(conn):
#         # pylint: disable=unused-argument
#         print('Got begin')
#         # We use this to detect and warn if we're initialized after sqlalchemy,
#         # which will cause the roundtrip count to be wrong
#         # TODO: Also call this on the twophase versions
#         get_context()['flask_events_in_database_session'] = True
#         store_database_timing(0)

#     @event.listens_for(Engine, 'commit')
#     def receive_commit(conn):
#         print('got commit')
#         get_context()['flask_events_in_database_session'] = False

#     begin_twophase(conn, xid)
#     commit_twophase(conn, xid, is_prepared)
#     engine_connect(conn, branch) # TODO: Use this to add database_new_connection=true
#     prepare_twophase(conn, xid)
#     release_savepoint(conn, name, context)
#     rollback_savepoint(conn, name, context)
#     rollback_twophase(conn, xid, is_prepared)
#     savepoint(conn, name)
#     @event.listens_for(Engine, 'rollback')
#     def receive_rollback(conn):
#         print('got rollback')
#         # TODO: test this with nested transactions, probably doesn't work (needs stack)
#         get_context()['flask_events_in_database_session'] = False
#         store_database_timing(0)
