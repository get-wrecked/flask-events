#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages


setup(
    name='Flask-Canonical',
    version='0.1.2',
    author='Tarjei Husøy',
    author_email='git@thusoy.com',
    url='https://github.com/megacool/flask-canonical',
    description="Easy canonical logging for Flask",
    packages=find_packages(),
    classifiers=[
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Logging',
        'Topic :: System :: Monitoring',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
)

