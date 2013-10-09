# -*- coding: utf8 -*-

import functools
from flask import session, request, redirect, url_for, make_response
from myapp import bcrypt

from .models import User

PERSIST_COOKIE_NAME = 'np'
PERSIST_MAX_AGE = User.COOKIE_PAIR_EXPIRE

def require_login(bookmarklet=False):
  """
  Login required decorator
  """

  def outer(f):
    @functools.wraps(f)
    def _(*args, **kwargs):
    
      # check session
      user_id = current_user_id()
      if user_id:
        return f(*args, **kwargs)

      else:
        # check persist cookie if session check failed
        persist_cookie = request.cookies.get(PERSIST_COOKIE_NAME, '')
        if ':' in persist_cookie:
          (user_id, digest) = persist_cookie.split(':')

          # check db for cookie validation
          expected_id = User.get_cookie_pair(digest)

          if user_id == expected_id:

            # valid, generate new cookie and allow login
            login(user_id)

            resp = f(*args, **kwargs)

            if type(resp) == str or type(resp) == unicode:
              resp = make_response(resp)

            User.remove_cookie_pair(digest)
            set_persist_cookie(resp, user_id)
            
            return resp

      url = url_for('login')
      if bookmarklet:
        url += "?b=1"

      return redirect(url)

    return _

  return outer


def j_require_login():
  """
  Login required decorator for a JSON request handler
  """

  def outer(f):
    @functools.wraps(f)
    def _(*args, **kwargs):
    
      user_id = current_user_id()
      if user_id:
        return f(*args, **kwargs)

      abort(403)

    return _

  return outer


def current_user_id():
  user_id = session.get('LOGIN_USER_ID', None)
  if user_id and User.exists(user_id):
    return user_id

  return None

def new_user(email, password):

  """
  Make a new user, save it and return user_id
  """

  # create new user and save it
  password_digest = bcrypt.generate_password_hash(password)
  user_id = User.new(email=email, screen_name='', password_digest=password_digest)

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

def update_password(user_id, password):
  """
  Update user's password
  """

  user = User.ref(user_id)
  if user:
    password_digest = bcrypt.generate_password_hash(password)
    user.update(password_digest=password_digest)

def authenticate(email, password):
  """
  Verify if Email and password are correct
  """
  user_id = User.get_id_by_email(email)
  if user_id:
    user = User.get(user_id, ['password_digest'])

    if bcrypt.check_password_hash(user.password_digest, password):
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


def set_persist_cookie(response, user_id):
  """
  Set persist cookie for user
  """
  user_ref = User.ref(user_id)
  digest = user_ref.make_cookie_pair()
  cookie = "%s:%s" % (user_id, digest)
  response.set_cookie(PERSIST_COOKIE_NAME, cookie, max_age=PERSIST_MAX_AGE, httponly=True)


def clear_persist_cookie(response):
  response.set_cookie(PERSIST_COOKIE_NAME, expires=1)
