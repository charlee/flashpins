#!/usr/bin/env python
# -*- coding:utf8 -*-

import os
import sys
from time import sleep

BASEDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASEDIR, 'myapp'))

from myapp import app

from queue.tasks import add

if __name__ == '__main__':
  rv = add.delay(1, 2)

  while not rv.ready:
    sleep(.1)

  print rv.return_value


