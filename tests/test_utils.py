import pytest

from flask_events.utils import humanize_size


@pytest.mark.parametrize('test_input,expected_output', [
    (1, '1B'),
    (1024, '1kB'),
    (1500000, '1.431MB'),
])
def test_humanize_size(test_input, expected_output):
    assert humanize_size(test_input) == expected_output
