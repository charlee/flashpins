# -*- coding: utf8 -*-

import re
from flask import request, redirect, render_template, url_for, abort
from core.user import require_login, current_user_id
from core.pin import new_pin
from core.models import Pin, User, Link
from myapp import app
from utils.common import make_context, paginate
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

  user_ref = User.ref(current_user_id())
  pin_ids = list(user_ref.pins())

  # pagination
  page = request.args.get('p', 1)
  (pin_ids, total_page) = paginate(pin_ids, page, app.config['PAGE_SIZE'])


  # get objects

  pins = Pin.mget(pin_ids)

  link_ids = [ pin.link_id for pin in pins ]
  links = Link.mget(link_ids)

  for pin, link in zip(pins, links):
    pin.link = link

  # get my tags
  my_tags = user_ref.tags()

  context = make_context({
    'pins': pins,
    'prev_page': (page - 1) if (page > 1) else 0,
    'next_page': (page + 1) if (page < total_page) else 0,
    'my_tags': my_tags,
  })
  return render_template('pins/me.html', **context)
