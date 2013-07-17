# -*- coding: utf8 -*-

import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = True


# redis db config
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None

# scss
#SCSS_STATIC_DIR =
#SCSS_ASSET_DIR =

# for views paging
PAGE_SIZE = 20

# for queue service
REDIS_QUEUE_KEY = 'fp:queue'
