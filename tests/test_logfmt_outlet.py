from collections import OrderedDict

import pytest
from testfixtures import LogCapture


from flask_events.outlets.logfmt import LogfmtOutlet


def test_logfmt(outlet):
    event_data = OrderedDict((('key', 'value'), ('foo', 'bar')))
    with LogCapture() as logs:
        outlet.handle(event_data, {}, {})

    assert len(logs.records) == 1
    record = logs.records[0]
    assert record.msg == 'key=value foo=bar' # measure#timing=0.123s'
    assert record.name == 'test_app.canonical'
    assert record.levelname == 'INFO'


def test_add_custom_value_with_spaces(outlet):
    with LogCapture() as logs:
        outlet.handle({'mykey': 'my custom value'}, {}, {})

    assert logs.records[0].msg == 'mykey="my custom value"'


@pytest.fixture
def outlet():
    return LogfmtOutlet('test_app')
