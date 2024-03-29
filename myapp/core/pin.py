import logging
import tempfile
import time
import lxml.html

from myapp.utils.crypt import urlhash
from .models import Link, User, Pin
from .user import current_user_id


log = logging.getLogger('core')


def new_pin(url, user_id, title='', desc='', tags=[], add_date=None, icon='', private=False):
  """
  New pin
  return None if already pinned this
  """
  # get default date
  if add_date is None:
    add_date = int(time.time())

  link_id = get_link_id(url, title=title, icon=icon, add_date=add_date, tags=tags)

  # get the link tilte to check if user changed the title
  link = Link.get(link_id, ['title'])
  if link.title == title:
    # save None if user does not change the title
    title = ''

  # check if user has already pinned this
  user_ref = User.ref(user_id)
  if not user_ref.has_link(link_id):
    
    # not pinned yet, pin it
    pin_id = Pin.new(link_id=link_id, user_id=user_id, taglist=','.join(tags), title=title, desc=desc, add_date=add_date, private=(1 if private else 0))

    # add pin & link references to user
    user_ref.add_pin(pin_id)
    user_ref.add_link(link_id)

    # increase link's pinned count
    link.inc_pin_count()

    # add tags to pin
    if tags:
      pin_ref = Pin.ref(pin_id)
      user_ref.update_pin_tags(pin_id, tags)

    return pin_id

  else:
    # has alreay pinned
    return None



def update_pin(pin_id, title=None, desc=None, tags=None, private=None):
  """
  Update pin with data
  None indicates no update on corresponding field
  """

  # prepare params
  params = {}

  if title is not None: params['title'] = title
  if desc is not None: params['desc'] = desc
  if private is not None: params['private'] = 1 if private else 0
  if tags is not None: params['taglist'] = ','.join(tags)

  # update pin
  pin_ref = Pin.ref(pin_id)

  if params:
    pin_ref.update(**params)

  # update pin tags
  if tags:
    pin = Pin.get(pin_id, ['user_id'])
    user_ref = User.ref(pin.user_id)

    old_tags = set(pin_ref.tags())
    new_tags = set(tags)
    added_tags = list(new_tags - old_tags)
    removed_tags = list(old_tags - new_tags)

    user_ref.update_pin_tags(pin_id, added_tags, removed_tags)


def get_link_id(url, title='', icon='', add_date=None, tags=[]):

  link_hash = urlhash(url)
  link_id = Link.get_by_hash(link_hash)

  now_ts = int(time.time())

  if not link_id:
    link_id = Link.new(hash=link_hash, title=title, url=url, icon=icon, add_date=add_date, access_date=now_ts)

  else:
    link_ref = Link.ref(id=link_id)
    link_ref.update(access_date=now_ts)

  link_ref = Link.ref(id=link_id)
  link_ref.accumulate_tags(tags)

  return link_id



def remove_pin(pin_id):
  """
  Delete a pin from database
  """

  pin = Pin.get(pin_id)

  if pin:

    # remove from user
    user_ref = User.ref(pin.user_id)
    user_ref.remove_pin(pin_id)
    user_ref.remove_link(pin.link_id)
    user_ref.update_pin_tags(pin.id, remove_tags=pin.tags())

    # decrease link counter
    link_ref = Link.ref(pin.link_id)
    link_ref.dec_pin_count()

    # remove pin
    Pin.remove(pin_id)


def run_import_pins_task(html_string):

  from myapp.queue.tasks import import_pins_task
  from myapp.queue import set_tmp_param

  key = set_tmp_param(html_string)

  import_pins_task.delay(current_user_id(), key)


def fill_pins(pin_ids):
  """
  return a list of fully retrieved pins
  """
  pins = Pin.mget(pin_ids)

  link_ids = [ pin.link_id for pin in pins ]
  links = Link.mget(link_ids)

  for pin, link in zip(pins, links):
    pin.link = link

  return pins
