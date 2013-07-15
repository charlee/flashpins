# -*- coding:utf8 -*-

from core.models import User
from core.user import current_user_id

def make_context(params):
    
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
