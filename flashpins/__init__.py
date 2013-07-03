# -*- coding: utf8 -*-

import os
import redis
from flask import Flask, render_template
from flask.ext.scss import Scss
from flask.ext.csrf import csrf
from flask.ext.bcrypt import Bcrypt
from flask.ext.coffee2js import coffee2js

# init global vars

app = Flask(__name__)
app.config.from_object('config')

# auto convert scss and coffee only in dev env
if app.debug:
  Scss(app)
  coffee2js(app, coffee_folder=os.path.join(app.root_path, 'assets/coffee'))

csrf(app)

bcrypt = Bcrypt(app)

# set app secret key for session
app.secret_key = 'xnrMPl.f$)wjqt2mE`%O+GBEWv9Ill#qog`HS3VSw!Smz$v.!%RWvTOW`JS#@28n';

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


