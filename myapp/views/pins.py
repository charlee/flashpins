# -*- coding: utf8 -*-

import re
from flask import request, redirect, render_template, url_for, abort
from myapp import app
from myapp.core.user import require_login, current_user_id
from myapp.core.pin import new_pin, fill_pins
from myapp.core.models import Pin, User, Link
from myapp.utils.common import make_context, paginate
from forms import PinAddForm, PinImportForm


@app.route('/i/<link_hash>')
def extract_url(link_hash):
  """
  Short url service
  """
  if not re.match(r'\w+', link_hash):
    abort(404)

  link_id = Link.get_by_hash(link_hash)
  link = Link.get(link_id, fields=['url'])
  if not link:
    abort(404)

  # record this access
  link.inc_view_count()

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

  from myapp.core.pin import run_import_pins_task

  form = PinImportForm(request.form)

  if request.method == 'POST' and form.validate():

    name = form.bookmark_file.name
    f = request.files.get(name)

    if f:
      filedata = f.read()
      run_import_pins_task(filedata)


  context = make_context({ 'form': form })
  return render_template('pins/import.html', **context)


@app.route('/me')
@require_login()
def me():
  """
  Show "My Pins" page
  """

  user_ref = User.ref(current_user_id())
  pin_count = user_ref.pin_count()

  # pagination
  page = request.args.get('p', 1)

  (start, end, page, total_page) = paginate(pin_count, page, app.config['PAGE_SIZE'])

  # get pins
  pin_ids = user_ref.pins(start, end)
  pins = fill_pins(pin_ids)

  # get my tags
  my_tags = user_ref.tags(with_count=True, total=50)

  context = make_context({
    'pins': pins,
    'prev_page': (page - 1) if (page > 1) else 0,
    'next_page': (page + 1) if (page < total_page) else 0,
    'my_tags': my_tags,
  })
  return render_template('pins/me.html', **context)


@app.route('/me/t/<tag>')
@require_login()
def my_tag_search(tag):
  """
  Tag search in current user's pins
  """
  user_ref = User.ref(current_user_id())
  pin_ids = user_ref.pins_in_tag(tag)

  # pagination
  pin_count = len(pin_ids)

  page = request.args.get('p', 1)
  (start, end, page, total_page) = paginate(pin_count, page, app.config['PAGE_SIZE'])
  pin_ids = pin_ids[start:end]

  # get pins
  pins = fill_pins(pin_ids)

  # get my tags
  my_tags = user_ref.tags(with_count=True)

  context = make_context({
    'pins': pins,
    'prev_page': (page - 1) if (page > 1) else 0,
    'next_page': (page + 1) if (page < total_page) else 0,
    'my_tags': my_tags,
  })

  return render_template('pins/me.html', **context)
