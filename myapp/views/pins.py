# -*- coding: utf8 -*-

import re
from flask import request, redirect, render_template, url_for, abort
from core.user import require_login, current_user_id
from core.pin import new_pin
from core.models import Pin, User, Link
from myapp import app
from utils.common import make_context
from forms import PinAddForm


@app.route('/i/<link_id>')
def extract_url(link_id):
  """
  Short url service
  """
  if not re.match(r'\w+', link_id):
    abort(404)

  link = Link.get(link_id, fields=['url'])
  if not link:
    abort(404)

  return redirect(link.url)

@app.route('/p/add', methods=['POST', 'GET'])
@require_login()
def add():
  """
  Add pin.
  """

  form = PinAddForm(request.form)

  if request.method == 'POST' and form.validate():
    title = form.title.data or ''
    url = form.url.data or ''
    desc = form.desc.data or ''

    new_pin(url=url, user_id=current_user_id(), title=title, desc=desc)

    return redirect(url_for('index'))

  context = make_context({ 'form': form })
  return render_template('pins/add.html', **context)




@app.route('/settings/import', methods=['POST', 'GET'])
@require_login()
def pins_import():
  """
  Import pins from browser bookmarks export
  """

  form = PinImportForm(request.form)

  if request.method == 'POST' and form.validate():

    # TODO
    pass

  context = make_context({ 'form': form })
  return render_template('pins/import.html', **context)


@app.route('/me')
@require_login()
def me():
  """
  Show "My Pins" page
  """

  # TODO: pagination

  user_ref = User.ref(current_user_id())
  pin_ids = user_ref.pins()
  pins = Pin.mget(pin_ids)

  link_ids = [ pin.link_id for pin in pins ]
  links = Link.mget(link_ids)

  for pin, link in zip(pins, links):
    pin.link = link

  context = make_context({ 'pins': pins })
  return render_template('pins/me.html', **context)
