# -*- coding:utf8 -*-

from flask import render_template, session
from myapp import app
from core.user import current_user_id
from core.models import User, Link

from utils.common import make_context

import pins
import users

from views.api.pins import api_pins

app.register_blueprint(api_pins, url_prefix='/j/pins')

@app.route('/')
def index():

  link_ids = Link.recent_links()
  links = Link.mget(link_ids)

  context = make_context({ 'links': links })

  return render_template('index.html', **context)

