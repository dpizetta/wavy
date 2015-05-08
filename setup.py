#! python
# -*- coding: utf-8 -*-

import codecs
import os
import re
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    # https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return codecs.open(os.path.join(here, *parts), 'r').read()

long_description = read('README.md')
classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: Python']

setup(name='Wavy',
      version=find_version("wavy", "gui_wavy.py"),
      description='Acquire sound from auxiliary/mic and save to dat',
      long_description=long_description,
      author='Daniel Cosmo Pizetta',
      author_email='daniel.pizett@usp.br',
      classifiers=classifiers,
      packages=['wavy',
                'wavy.images'],
      package_data={'data_wavy': ['README.md',
                                  '*.png',
                                  '*.ui']},
      scripts=['run.py'],
      entry_points={
          "console_scripts": [
              "wavy=run:main"
          ],
      }

      )
