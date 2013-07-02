#!/usr/bin/env python
"""
Creates shell using IPython
"""

import os
import sys

from werkzeug import script
from flashpins import *

def make_shell():
  return dict(app=app, rds=rds)

if __name__ == "__main__":

  BASEDIR = os.path.dirname(os.path.abspath(__file__))
  sys.path.insert(0, os.path.join(BASEDIR, 'flashpins'))

  script.make_shell(make_shell, use_ipython=True)()
