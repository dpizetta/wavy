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
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, *parts), 'r').read()


long_desc = ''

with open('README.md') as f:
    long_desc = f.read()

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: Python']

setup(name='wavytool',
      version=find_version("wavytool", "__init__.py"),
      description='Simple GUI that acquires data from input devices, plot and export files.',
      long_description=long_desc,
      long_description_content_type='text/markdown',
      url='https://github.com/dpizetta/wavy',
      author='Daniel Cosmo Pizetta',
      author_email='daniel.pizett@usp.br',
      classifiers=classifiers,
      packages=['wavytool',
                'wavytool.images'],
      package_data={'wavytool_data': ['README.md',
                                      '*.png',
                                      '*.ui']},
      entry_points={
          "gui_scripts": [
              "wavytool=wavytool.__main__:main"]},
      install_requires=['qtpy>=1.4',
                        'numpy>=1.13',
                        'pyqtgraph>=0.10',
                        'pyaudio>=0.2']
      )
