#!/usr/bin/env python
# -*- coding:utf8 -*-

import os
import sys

if __name__ == '__main__':

  BASEDIR = os.path.dirname(os.path.abspath(__file__))
  sys.path.insert(0, os.path.join(BASEDIR, 'myapp'))

  from myapp import app

  app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=8000)
