#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages


version_file = os.path.join(os.path.dirname(__file__), 'flask_events', '_version.py')
with open(version_file) as fh:
    version_file_contents = fh.read().strip()
    version_match = re.match(r"__version__ = '(\d\.\d\.\d.*)'", version_file_contents)
    version = version_match.group(1)

setup(
    name='Flask-Events',
    version=version,
    author='Tarjei Husøy',
    author_email='git@thusoy.com',
    url='https://github.com/get-wrecked/flask-events',
    description="Easy structured logging and metrics collection for Flask",
    install_requires=[
        'libhoney >= 1.3.0',
    ],
    packages=find_packages(),
    license='Hippocratic-2.1',
    classifiers=[
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        'Development Status :: 7 - Inactive',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: System :: Logging',
        'Topic :: System :: Monitoring',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
)

