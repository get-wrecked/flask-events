from celery import Celery, signals
import pytest
from flask import Flask

from flask_events import Events

from .conftest import CapturingOutlet

# pylint: disable=redefined-outer-name

celery = Celery('tasks')


@celery.task(name='test_task')
def fake_test_task(posarg, *args, keyed=None, **kwargs): # pylint: disable=unused-argument
    pass


@celery.task(name='test-pos-or-kwargs')
def pos_or_kwargs(posarg, either=None, *varargs): # pylint: disable=unused-argument
    pass


@pytest.mark.usefixtures('clean_celery_signals')
def test_celery_app(celery_app):
    signals.task_prerun.send(sender='foo', task=fake_test_task)
    signals.task_postrun.send(sender='foo')

    assert celery_app.test_outlet.event_data['task'] == 'test_task'


@pytest.mark.usefixtures('clean_celery_signals')
def test_celery_args(celery_app):
    signals.task_prerun.send(sender='foo', task=fake_test_task,
        args=['firstarg', 'secondarg'])
    signals.task_postrun.send(sender='foo')

    assert celery_app.test_outlet.event_data['posarg'] == 'firstarg'
    assert celery_app.test_outlet.event_data['args_0'] == 'secondarg'


@pytest.mark.usefixtures('clean_celery_signals')
def test_celery_without_autoarg(celery_app):
    celery_app.events.autoadd_celery_args = False
    print('settinf alse')
    # import pdb; pdb.set_trace()
    signals.task_prerun.send(sender='foo', task=fake_test_task,
        args=['firstarg', 'secondarg'])
    signals.task_postrun.send(sender='foo')

    assert 'posarg' not in  celery_app.test_outlet.event_data
    assert 'args_0' not in  celery_app.test_outlet.event_data


@pytest.mark.usefixtures('clean_celery_signals')
def test_celery_custom_vararg(celery_app):
    signals.task_prerun.send(sender='foo', task=pos_or_kwargs,
        args=['firstarg', 'secondarg', 'thirdarg', 'fourtharg'])
    signals.task_postrun.send(sender='foo')

    assert celery_app.test_outlet.event_data['posarg'] == 'firstarg'
    assert celery_app.test_outlet.event_data['either'] == 'secondarg'
    assert celery_app.test_outlet.event_data['varargs_0'] == 'thirdarg'
    assert celery_app.test_outlet.event_data['varargs_1'] == 'fourtharg'


@pytest.mark.usefixtures('clean_celery_signals')
def test_celery_kwargs(celery_app):
    signals.task_prerun.send(sender='foo', task=fake_test_task,
        kwargs={'somekey': 'somevalue'})
    signals.task_postrun.send(sender='foo')

    assert celery_app.test_outlet.event_data['somekey'] == 'somevalue'


@pytest.fixture
def celery_app():
    app = Flask('test_app')
    app.test_outlet = CapturingOutlet()
    app.events = Events()
    app.events.init_celery_app(app)
    app.events.outlets = [app.test_outlet]
    return app


@pytest.fixture
def clean_celery_signals():
    try:
        yield
    finally:
        clean_celery_signal_receivers(signals.task_prerun)
        clean_celery_signal_receivers(signals.task_postrun)


def clean_celery_signal_receivers(signal):
    for receiver in signal._live_receivers(None): # pylint: disable=protected-access
        signal.disconnect(receiver)
