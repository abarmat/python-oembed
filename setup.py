#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def publish():
    """Publish to Pypi"""
    os.system("python setup.py sdist upload")

if sys.argv[-1] == "publish":
    publish()
    sys.exit()

version = '0.2.2'

setup(
    name='python-oembed',
    version=version,
    description='OEmbed consumer library for Python',
    long_description=open('README.markdown').read() + '\n\n' + open('HISTORY.rst').read(),
    author='Ariel Barmat',
    author_email='abarmat@gmail.com',
    url='http://github.com/abarmat/python-oembed',
    packages=['oembed'],
    license='MIT',
    classifiers = ( 
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
    ),
    keywords='oembed python api'    
)
