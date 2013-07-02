# -*- coding:utf8 -*-

from flask import render_template, request, redirect
from flashpins import app
from core.user import authenticate, login as user_login, logout as user_logout

from forms import LoginForm


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

  return render_template('users/login.html', form=form)
  


@app.route('/logout'):
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
    password = form.email.password

  return render_template('users/register.html', form=form)
