# -*- coding:utf8 -*-

from flask import render_template, session
from myapp import app
from core.user import current_user_id
from core.models import User

from utils.common import make_context

import pins
import users

@app.route('/')
def index():

  user_id = current_user_id()
  if user_id:
    user = User.get(user_id)
  else:
    user = None

  context = make_context({})

  return render_template('index.html', **context)

