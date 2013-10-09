# -*- coding:utf8 -*-

from flask import render_template, request, redirect, url_for, g
from myapp import app
from myapp.core.user import new_user, update_password, current_user_id, require_login, authenticate, login as user_login, logout as user_logout
from myapp.core.models import User
from myapp.utils.common import make_context

from forms import LoginForm, RegisterForm, SettingsAccountForm, SettingsProfileForm

PERSIST_COOKIE_NAME = 'np'
PERSIST_MAX_AGE = User.COOKIE_PAIR_EXPIRE

@app.before_request
def check_login_cookie():
  """
  Check if the persist cookie is valid
  log user in if cookie is valid
  """

  # shortcut if already logged in
  if current_user_id() is not None:
    return

  # check login cookie
  persist_cookie = request.cookies.get(PERSIST_COOKIE_NAME, '')

  if ':' in persist_cookie:
    (user_id, digest) = persist_cookie.split(':')

    # check db for cookie validation
    expected_id = User.get_cookie_pair(digest)

    if user_id == expected_id:

      # valid, generate new cookie and allow login
      user_login(user_id)

      User.remove_cookie_pair(digest)

      # set cookie flag, used to set cookie in after_request() functions
      g._persist_cookie_user = user_id
      


@app.after_request
def set_login_cookie(response):
  """
  Set persist cookie for user
  """
  cookie_user_id = getattr(g, '_persist_cookie_user', None)

  if cookie_user_id is not None:

    g._persist_cookie_user = None

    user_ref = User.ref(cookie_user_id)

    if user_ref is not None:
      
      digest = user_ref.make_cookie_pair()
      cookie = "%s:%s" % (cookie_user_id, digest)
      response.set_cookie(PERSIST_COOKIE_NAME, cookie, max_age=PERSIST_MAX_AGE, httponly=True)

  return response
  

@app.route('/login', methods=['POST', 'GET'])
def login():
  """
  User login
  """
  is_bookmarklet = request.args.get('b')

  form = LoginForm(request.form)

  if request.method == 'POST' and form.validate():
    email = form.email.data
    password = form.password.data
    remember = form.remember.data

    user_id = authenticate(email, password)
    if user_id:
      user_login(user_id)

      resp = redirect(url_for('index'))

      if remember:
        g._persist_cookie_user = user_id

      return resp


  context = make_context({ 'form': form })

  if is_bookmarklet:
    tmpl = 'users/bookmarklet-login.html'
  else:
    tmpl = 'users/login.html'

  return render_template(tmpl, **context)
  


@app.route('/logout')
def logout():
  """
  User logout
  """
  user_logout()

  # clear cookie
  resp = redirect(url_for('index'))
  resp.set_cookie(PERSIST_COOKIE_NAME, expires=1)
  return resp




@app.route('/register', methods=['POST', 'GET'])
def register():
  """
  User register
  """

  form = RegisterForm(request.form)

  if request.method == 'POST' and form.validate():
    email = form.email.data
    password = form.password.data

    user_id = new_user(email, password)

    user_id = authenticate(email, password)
    if user_id:
      user_login(user_id)
      return redirect(url_for('index'))

  context = make_context({ 'form': form })
  return render_template('users/register.html', **context)


@app.route('/settings', methods=['POST', 'GET'])
@require_login()
def settings():
  """
  Account settings
  """

  form = SettingsProfileForm(request.form)
 
  if request.method == 'POST' and form.validate():
    screen_name = form.screen_name.data
    user_ref = User.ref(current_user_id())
    user_ref.update(screen_name=screen_name)

    return redirect(url_for('settings'))

  context = make_context({ 'form': form })
  return render_template('users/settings.html', **context)


@app.route('/settings/account', methods=['POST', 'GET'])
@require_login()
def account():
  """
  Change password, etc
  """

  form = SettingsAccountForm(request.form)

  if request.method == 'POST' and form.validate():
    
    password = form.password.data
    update_password(current_user_id(), password)

    return redirect(url_for('account'))

  context = make_context({ 'form': form })
  return render_template('users/account.html', **context)




