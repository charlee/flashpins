# -*- coding:utf8 -*-

from wtforms import Form, TextField, PasswordField, FileField, validators


class LoginForm(Form):
  email = TextField('Email')
  password = PasswordField('Password')


class RegisterForm(Form):
  email = TextField('Email', [validators.Email()])
  password = PasswordField('Password', [validators.Required(), validators.EqualTo('confirm_password', message='Passwords does not match')])
  confirm_password = PasswordField('Confirm Password')


class SettingsProfileForm(Form):
  screen_name = TextField()


class SettingsAccountForm(Form):
  password = PasswordField('Password', [validators.Required(), validators.EqualTo('confirm_password', message='Passwords does not match')])
  confirm_password = PasswordField('Confirm Password')


class PinAddForm(Form):
  title= TextField()
  url = TextField()
  desc = TextField()


class PinImportForm(Form):
  bookmark_file = FileField('Bookmark File')
