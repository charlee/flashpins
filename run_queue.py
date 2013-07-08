#!/usr/bin/env python

import os
import sys

BASEDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASEDIR, 'myapp'))

from myapp import app
from queue import queue_daemon

queue_daemon(app)
