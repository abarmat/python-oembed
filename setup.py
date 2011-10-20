#!/usr/bin/python
#
# Copyright 2008 Ariel Barmat.

'''The setup and build script for the python-oembed library.'''

__author__ = 'abarmat@gmail.com'
__version__ = '0.2.0'


# The base package metadata to be used by both distutils and setuptools
METADATA = dict(
  name = "python-oembed",
  version = __version__,
  py_modules = ['oembed'],
  author='Ariel Barmat',
  author_email='abarmat@gmail.com',
  long_description='A Python library that implements an OEmbed consumer to use with OEmbed providers.',
  license='MIT License',
  url='http://code.google.com/p/python-oembed/',
  keywords='oembed python api',
)

# Extra package metadata to be used only if setuptools is installed
SETUPTOOLS_METADATA = dict(
  install_requires = ['setuptools', 'simplejson'],
  include_package_data = True,
  classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Internet',
  ],
  test_suite = 'oembed_test.suite',
)

import sys
if sys.version < '2.5':
        SETUPTOOLS_METADATA['install_requires'].append('ElementTree')
        SETUPTOOLS_METADATA['install_requires'].append('cElementTree')

def Read(file):
  return open(file).read()

def BuildLongDescription():
  return '\n'.join([Read('CHANGES')])

def Main():
  # Build the long_description from the README and CHANGES
  METADATA['long_description'] = BuildLongDescription()

  # Use setuptools if available, otherwise fallback and use distutils
  try:
    import setuptools
    METADATA.update(SETUPTOOLS_METADATA)
    setuptools.setup(**METADATA)
  except ImportError:
    import distutils.core
    distutils.core.setup(**METADATA)


if __name__ == '__main__':
  Main()
