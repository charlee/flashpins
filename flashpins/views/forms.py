# -*- coding:utf8 -*-

from wtforms import Form, TextField, PasswordField


class LoginForm(Form):
  email = TextField('Email')
  password = PasswordField('Password')


class RegisterForm(form):
  email = TextField('Email')
  password = PasswordField('Password')
  confirm_password = PasswordField('Confirm Password')

