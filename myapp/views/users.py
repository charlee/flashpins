# -*- coding:utf8 -*-

from flask import render_template, request, redirect, url_for
from myapp import app
from core.user import new_user, require_login, authenticate, login as user_login, logout as user_logout
from core.models import User
from utils.common import make_context

from forms import LoginForm, RegisterForm, SettingsAccountForm, SettingsProfileForm


@app.route('/login', methods=['POST', 'GET'])
def login():
  """
  User login
  """

  form = LoginForm(request.form)

  if request.method == 'POST' and form.validate():
    email = form.email.data
    password = form.email.password
    user_id = authenticate(email, password)
    if user_id:
      user_login(user_id)
      return redirect(url_for('index'))


  context = make_context({ 'form': form })
  return render_template('users/login.html', **context)
  


@app.route('/logout')
def logout():
  """
  User logout
  """
  user_logout()
  return redirect(url_for('index'))



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
def account(request):
  """
  Change password, etc
  """

  form = SettingsAccountForm(request.form)

  if request.method == 'POST' and form.validate():
    
    password = form.password.data
    # TODO

    return redirect(url_for('account'))

  context = make_context({ 'form': form })
  return render_template('users/account.html', **context)




