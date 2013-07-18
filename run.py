#!/usr/bin/env python
# -*- coding:utf8 -*-

from myapp import app

if __name__ == '__main__':

  app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=8000)
