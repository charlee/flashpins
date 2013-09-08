from . import queue_task, get_tmp_param

import lxml
from datetime import datetime

from myapp.core.models import User, Pin, Link
from myapp.core.pin import new_pin


@queue_task
def import_pins_task(user_id, file_key):

  html_string = get_tmp_param(file_key)

  root = lxml.html.fromstring(html_string)
  for t in root.iterlinks():
    a = t[0]

    icon = a.get('icon', '')
    url = a.get('href')
    add_date = a.get('add_date')

    # tags property from delicious
    tags = filter(None, a.get('tags', '').split(','))

    # private property from delicious
    private = (a.get('private', '0') != '0')
      
    title = a.text or ''

    if url:

      try:
        add_date = int(add_date)
      except:
        add_date = int(time.time())

      new_pin(url, user_id, title=title, tags=tags, add_date=add_date, icon=icon, private=private)


