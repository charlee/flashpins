# -*- coding: utf8 -*-

from flask import request, redirect, render_template
from core.user import require_login, current_user_id
from core.models import Pin, User
from flashpins import app
from utils.common import make_context
from forms import PinAddForm

@app.route('/p/add', methods=['POST', 'GET'])
@require_login()
def add():
  """
  Add pin.
  """

  form = PinAddForm(request.form)

  if request.method == 'POST' and form.validate():
    title = form.title.data
    url = form.url.data

    new_pin(title=title, url=url, user_id=current_user_id())

    return redirect(url_for('/'))

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

  context = make_context({ 'pins': pins })
  return render_template('pins/me.html', **context)
