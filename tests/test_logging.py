import re
from collections import OrderedDict

from testfixtures import LogCapture

ITEM_RE = re.compile(r'([\w#]+)=(?:"([^"]*)"|([\w./-]*))')


def test_logger_unconfigured(client):
    with LogCapture() as logs:
        response = client.get('/')
    assert response.status_code == 200

    assert_logged(logs, 'fwd', '127.0.0.1')
    assert_logged(logs, 'tag', 'main_route')
    assert_logged(logs, 'method', 'GET')
    assert get_item(logs, 'request_user_agent').startswith('werkzeug')
    assert_logged(logs, 'status', '200')
    assert_matches(logs, 'measure#timing_total', r'^0.\d{3}s$')


def test_custom_tag(app):
    with LogCapture() as logs:
        with app.test_request_context('/'):
            app.preprocess_request()
            app.canonical_logger.tag = 'mytag'

    assert_logged(logs, 'tag', 'mytag')


def test_includes_request_id(client):
    with LogCapture() as logs:
        response = client.get('/', headers={
            'x-request-id': 'myrequestid',
        })
    assert response.status_code == 200

    assert_logged(logs, 'request_id', 'myrequestid')


def test_add_custom_value(app):
    with LogCapture() as logs:
        with app.test_request_context('/'):
            app.preprocess_request()
            app.canonical_logger.add('mykey', 'my-custom-value')

    assert_logged(logs, 'mykey', 'my-custom-value')


def test_add_custom_value_with_spaces(app):
    with LogCapture() as logs:
        with app.test_request_context('/'):
            app.preprocess_request()
            app.canonical_logger.add('mykey', 'my custom value')

    assert_logged(logs, 'mykey', 'my custom value')
    assert 'mykey="my custom value"' in logs.records[-1].msg


def test_add_sample(app):
    with LogCapture() as logs:
        with app.test_request_context('/'):
            app.preprocess_request()
            app.canonical_logger.add_sample('counter', 3)

    assert_logged(logs, 'sample#counter', '3')


def test_aborted_view(client):
    with LogCapture() as logs:
        response = client.get('/abort')
    assert response.status_code == 503

    assert_logged(logs, 'status', '503')


def test_invalid_utf8(client):
    with LogCapture() as logs:
        response = client.get(b'/?param=\xEA')
        assert response.status_code == 200

    assert 'path="/?param=\\xea"' in logs.records[-1].msg


def assert_logged(logs, key, value):
    item = get_item(logs, key)
    assert item == value


def assert_matches(logs, key, regex):
    item = get_item(logs, key)
    assert re.match(regex, item) is not None


def get_item(logs, key):
    last_record = logs.records[-1]

    # sanity check that we got the correct record
    assert last_record.levelname == 'INFO'
    assert last_record.name == 'test_app.canonical'

    return parse(last_record.msg)[key]


def parse(line):
    parsed = OrderedDict()
    for match in ITEM_RE.finditer(line):
        value = match.group(2) or match.group(3)
        parsed[match.group(1)] = value
    return parsed


def test_parse():
    log_line = 'fwd=127.0.0.1 user_agent="some agent/1.0.0"'
    assert parse(log_line) == {
        'fwd': '127.0.0.1',
        'user_agent': 'some agent/1.0.0',
    }
