import logging

import lxml.html
from utils.crypt import urlhash
from models import Link, User, Pin


log = logging.getLogger('core')


def new_pin(url, user_id, title='', desc='', tags=[], add_date=None, icon='', private=False):
  """
  New pin
  return None if already pinned this
  """
  link_id = get_link_id(url, title=title, icon=icon, add_date=add_date)

  # get the link tilte to check if user changed the title
  link = Link.get(link_id, ['title'])
  if link.title == title:
    # save None if user does not change the title
    title = ''

  # check if user has already pinned this
  user_ref = User.ref(user_id)
  if not user_ref.has_link(link_id):
    
    # not pinned yet, pin it
    pin_id = Pin.new(link_id=link_id, user_id=user_id, title=title, desc=desc, add_date=add_date, private=(1 if private else 0))

    # add pin & link references to user
    user_ref.add_pin(pin_id)
    user_ref.add_link(link_id)

    # increase link's pinned count
    link.inc_pinned_count()

    # add tags to pin
    if tags:
      pin_ref = Pin.ref(pin_id)
      pin_ref.update_tags(tags)
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

    pin_ref.update_tags(added_tags, removed_tags)
    user_ref.update_pin_tags(pin_id, added_tags, removed_tags)


def get_link_id(url, title='', icon='', add_date=None):

  link_id = urlhash(url)

  if not Link.exists(link_id):
    link_id = Link.new(id=link_id, title=title, url=url, icon=icon, add_date=add_date)

  return link_id



def remove_pin(pin_id):
  """
  Delete a pin from database
  """

  pin = Pin.get(pin_id)

  if pin:

    # remove user ref
    user_ref = User.ref(pin.user_id)
    user_ref.remove_pin(pin_id)
    user_ref.remove_link(pin.link_id)

    # decrease link counter
    link_ref = Link.ref(pin.link_id)
    link_ref.dec_pinned_count()

    # remove pin
    Pin.remove(pin_id)



def import_pins(html_string):
    """
    Import all the links in a bookmark html.
    """
    
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
                ts = int(add_date)
                d = datetime.fromtimestamp(ts, utc)
            except:
                d = datetime.utcnow().replace(tzinfo=utc)

            yield(url, d, icon, title, tags, private)

