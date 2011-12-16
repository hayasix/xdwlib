#!/usr/bin/env python2.6
#vim:fileencoding=cp932:fileformat=dos

import sys
import os

from xdwlib.common import cp
from xdwlib.xdwfile import extract_sfx


for source in sys.argv[1:]:
    extract_sfx(cp(source))
