# -*- coding: utf8 -*-

import redis
from flask import Flask, render_template


# init global vars

app = Flask(__name__)
app.config.from_object('config')

rds = redis.StrictRedis(host=app.config['REDIS_HOST'],
                        port=app.config['REDIS_PORT'],
                        db=app.config['REDIS_DB'],
                        password=app.config['REDIS_PASSWORD'])


# import views

import flashpins.views


# common handlers

@app.errorhandler(404)
def not_found(error):
  return render_template('404.html'), 404


