#!/usr/bin/env python

from myapp import app
from myapp.queue import queue_daemon

queue_daemon(app)
