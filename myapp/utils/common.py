# -*- coding:utf8 -*-

import random

def make_context(params):
    
  from myapp.core.models import User
  from myapp.core.user import current_user_id

  context = {}

  user_id = current_user_id()
  user = User.get(user_id)

  if user:
    context.update({ 'user': user })

  context.update(params)

  return context


def paginate(size, page, page_size):
  """
  paginate the objects
    ids: object ids that need to be paginated
    page: page number
    page_size: page_size

  return:
    start, end, total_page
  """
  total_page = size / page_size

  if total_page * page_size > size:
    total_page += 1

  # normalize current page number
  if type(page) == str or type(page) == unicode:
    if page.isdigit():
      page = int(page)
    else:
      page = 1
  if page < 1: page = 1
  if page > total_page: page = total_page

  # output
  start = (page - 1) * page_size
  end = start + page_size if page < total_page else size

  return start, end, page, total_page


def score_list(l):
  """
  Add score "1" to each element of the list.
  Used by redis.ZADD
  """
  return [ x for y in l for x in (1, y) ]


def random_string(length, chars=None):
  """
  make a random string
    chars: string that contains all available chars
  """
  if chars is None:
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

  return ''.join(random.choice(chars) for x in range(length))

