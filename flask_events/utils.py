UNITS = (
    (2**40.0, 'TB'),
    (2**30.0, 'GB'),
    (2**20.0, 'MB'),
    (2**10.0, 'kB'),
    (0.0, 'B'),
)


def humanize_size(s):
    """Convert bytes to human-readable form (e.g. kB, MB).
    Lifted from celery.utils.debug
    """
    return next(
        '{0}{1}'.format(_hfloat(s / div if div else s), unit)
        for div, unit in UNITS if s >= div
    )


def _hfloat(f, p=4):
    """Convert float to value suitable for humans.

    :keyword p: Float precision.

    """
    i = int(f)
    return i if i == f else '{0:.{p}}'.format(f, p=p)
