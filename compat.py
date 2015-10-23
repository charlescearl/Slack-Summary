# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from sys import version_info


PY3 = version_info[0] == 3

if PY3:
    bytes = bytes
    unicode = str
else:
    bytes = str
    unicode = unicode
string_types = (bytes, unicode,)
