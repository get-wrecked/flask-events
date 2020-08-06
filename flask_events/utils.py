UNITS = (
    (2**40.0, 'TB'),
    (2**30.0, 'GB'),
    (2**20.0, 'MB'),
    (2**10.0, 'kB'),
    (0.0, 'B'),
)


def humanize_size(size):
    """Convert bytes to human-readable form (e.g. kB, MB).
    Lifted from celery.utils.debug
    """
    return next(
        '{0}{1}'.format(_hfloat(size / div if div else size), unit)
        for div, unit in UNITS if size >= div
    )


def _hfloat(value, precision=4):
    """Convert float to value suitable for humans.

    :keyword precision: Float precision.

    """
    i = int(value)
    return i if i == value else '{0:.{precision}}'.format(value, precision=precision)
