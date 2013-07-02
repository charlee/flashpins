# -*- coding: utf8 -*-

import functools
from flask import session


def new_user(email, password):

    """
    Make a new user, save it and return user_id
    """

    hasher = BCryptPasswordHasher()

    # create new user and save it
    password_digest = hasher.encode(password, hasher.salt())
    user_id = User.new(email=email, password_digest=password_digest)

    return user_id

  
def set_screen_name(user_id, screen_name):
  """
  Change user screen name
  Return True if succeed; False if failed (screen_name exists, or user not exists)
  """

  # check screen_name
  if User.get_id_by_screen_name(screen_name):
    return False

  # update user screen_name
  user_ref = User.ref(user_id)

  if not user_ref:
    return False

  user_ref.update(screen_name=screen_name)

  return True

def authenticate(email, password):
  """
  Verify if Email and password are correct
  """
  user_id = User.get_id_by_email(email)
  if user_id:
    user = User.get(user_id, ['password_digest'])
    hasher = BCryptPasswordHasher()
    if hasher.verify(password, user.password_digest):
      return user_id

    return False
  

def login(user_id):
  """
  Login user by email
  """

  session['LOGIN_USER_ID'] = user_id


def logout():
  """
  Logout user
  """
  session.pop('LOGIN_USER_ID', None)
