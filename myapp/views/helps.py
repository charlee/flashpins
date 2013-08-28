# -*- coding: utf8 -*-

from flask import request, render_template
from myapp import app
from myapp.utils.common import make_context

@app.route('/help')
def help():
  """
  Help page
  """

  context = make_context({
    'host': request.host_url
  })

  return render_template('helps/main.html', **context)
