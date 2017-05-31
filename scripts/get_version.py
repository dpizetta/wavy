#!/usr/bin python2

"""A simple python script template.
"""

import os
import sys
import codecs
import re


here = os.path.abspath(os.path.join('../', os.path.dirname(__file__)))

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


version=find_version("wavy", "gui_wavy.py")
print version

with open('got_version.temp', 'w') as f:
    f.write(version)


