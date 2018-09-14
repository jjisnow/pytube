#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains setup instructions for pytube."""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('LICENSE') as readme_file:
    license = readme_file.read()

setup(
    name='pytube',
    version='9.2.3',
    author='jjisnow',
    author_email='jjisnow@gmail.com',
    packages=['pytube', 'pytube.contrib'],
    url='https://github.com/jjisnow/pytube',
    license=license,
    entry_points={
        'console_scripts': [
            'pytube = pytube.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Multimedia :: Video',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Terminals',
        'Topic :: Utilities',
    ],
    description=('A pythonic library for downloading YouTube Videos.'),
    long_description=readme,
    zip_safe=True,
)
