#!/usr/bin/env python
"""
Creates shell using IPython
"""

from werkzeug import script

def make_shell():
  return dict(app=app, rds=rds)

if __name__ == "__main__":

  from myapp import *

  script.make_shell(make_shell, use_ipython=True)()
