# -*- coding: utf8 -*-

"""
Define common ops for data models
"""


#######################################################################
# DESIGN PRINCIPLE
#
# 1. Class must deal with all keys related to itself
# 2. Don't touch objects from other classes (these should go to core.*, not models)
# 3. Instance methods should not rely on fields other than id;
#    so that a reference returned by Class.ref() can call all instance methods
#
#######################################################################

import re
from myapp import rds 

# Link


class BaseModelMeta(type):

  def __init__(cls, name, bases, attrs):
    
    fields = {}

    # inherit fields from parent
    for base in bases:
      if hasattr(base, 'fields'):
        fields.update(base.fields)

    # overwrite base fields with own `fields`
    if attrs.has_key('fields'):
      fields = attrs['fields']

    # add extra fields if `extra_fields` defined
    if attrs.has_key('extra_fields'):
      fields.update(attrs['extra_fields'])

    cls.fields = fields

    # prepare for key name
    table_name = re.sub(r'([A-Z])', r'_\1', name)
    table_name = table_name[1:] if table_name[0] == '_' else table_name
    table_name = table_name.lower()

    # generate redis key name
    if not attrs.has_key('KEY'):
      cls.KEY = 'fp:' + table_name + ':%s'
      
    # generate auto_increment key name
    if not attrs.has_key('KEY_INCR'):
      cls.KEY_INCR = 'fp:' + table_name + ',incr'


class BaseHash:
  """Hash-type base model class"""

  __metaclass__ = BaseModelMeta

  def __init__(self, id, *args, **kwargs):

    # id is always str
    self.id = str(id)

    for field in self.fields.keys():

      default = self.fields[field]
      v = kwargs.get(field, str(default))

      # convert str to unicode
      if type(v) == str:
        v = v.decode('utf-8')

      setattr(self, field, v)

  def __repr__(self):
    keys = self.fields.keys()
    values = [getattr(self, key).encode('utf-8') for key in keys]
    attrs = ', '.join('%s=%s' % pair for pair in zip(keys, values))

    return "<%s: id=%s, %s>" % (self.__class__.__name__, self.id, attrs)

  def __unicode__(self):
    return self.__repr__()

  def as_hash(self):
    h = { 'id': self.id }
    for field in self.fields.keys():
      h[field] = getattr(self, field)
    return h
      
  @classmethod
  def get(cls, id, fields=None):
    """
    Get a single object
    """
    if not id:
      return

    if not fields:
      fields = cls.fields.keys()

    if not cls.exists(id):
      return None

    result = rds.hmget(cls.KEY % id, fields)

    return cls(id, **dict(zip(fields, result)))

  @classmethod
  def mget(cls, ids, fields=None):
    """
    Get multiple objects (with pipeline)
    """
    if not ids:
      return []

    if not fields:
      fields = cls.fields.keys()

    p = rds.pipeline()
    for id in ids:
      p.hmget(cls.KEY % id, fields)

    result = p.execute()

    return map(lambda pair: cls(pair[0], **dict(zip(fields, pair[1]))),
               zip(ids, result))

  @classmethod
  def exists(cls, id):
    """
    Check if an id exists in the database
    """
    return rds.exists(cls.KEY % id)

  @classmethod
  def _filter_params(cls, params):
    """
    Filter kwargs to pre-defined fields
    """
    return dict((k, v) for (k, v) in params.iteritems() if k in cls.fields)

  @classmethod
  def ref(cls, id):
    """
    Get the object reference by id.
    This method makes sure that the id exists, but will not fill any fields.
    """
    if cls.exists(id):
      return cls(id)
    else:
      return None


  @classmethod
  def new(cls, id=None, **kwargs):
    """
    Add a new object and return added id
    """
    
    if not id:
      # generate auto increment id
      id = rds.incr(cls.KEY_INCR)
      while cls.exists(id):
        id = rds.incr(cls.KEY_INCR)

    # add data to db
    params = cls._filter_params(kwargs)
    rds.hmset(cls.KEY % id, params)

    return id
    

  def update(self, **kwargs):
    """
    Update current object
    """
    
    # update data to db
    params = self._filter_params(kwargs)
    rds.hmset(self.KEY % self.id, params)

    # update object
    for k, v in kwargs.iteritems():
      setattr(self, k, v)

  @classmethod
  def remove(cls, id):
    """
    Delete specified object
    """
    rds.delete(cls.KEY % id)



class Link(BaseHash):

  KEY_PIN_COUNT = 'fp:link:%s:pinned_count'
  KEY_VIEW_COUNT = 'fp:link:%s:viewed_count'

  fields = {
    'title': '',
    'url': '',
    'icon': '',
    'add_date': 0,
  }

  def pin_count(self):
    return rds.get(self.KEY_PIN_COUNT % self.id)


  def view_count(self):
    return rds.get(self.KEY_VIEW_COUNT% self.id)


  def inc_pin_count(self):
    rds.incr(self.KEY_PIN_COUNT % self.id)


  def dec_pin_count(self):
    # TODO: make sure counter >= 0
    rds.decr(self.KEY_PIN_COUNT % self.id)
    

  def inc_view_count(self):
    rds.incr(self.KEY_VIEW_COUNT % self.id)


  def dec_view_count(self):
    rds.dec(self.KEY_VIEW_COUNT % self.id)


  @classmethod
  def remove(cls, id):
    """
    Delete a link
    """
    super(Link, cls).remove(id)

    # clear the counters
    p.delete(cls.KEY_PIN_COUNT % id, cls.KEY_VIEW_COUNT % id)
    

      
class Pin(BaseHash):

  KEY_TAGS = 'fp:pin:%s:tags'

  fields = {
    'title': '',
    'desc': '',
    'link_id': '',
    'user_id': 0,
    'add_date': 0,
    'private': 0,
  }

  def update_tags(self, add_tags=None, remove_tags=None):
    """
    Add or remove tags to current pin
    """
    if add_tags:
      rds.sadd(self.KEY_TAGS % self.id, *add_tags)

    if remove_tags:
      rds.srem(self.KEY_TAGS % self.id, *remove_tags)
      

  def tags(self):
    """
    return tags (list)
    """
    if not hasattr(self, '_tags') or self._tags is None:
      self._tags = [ x.decode('utf-8') for x in list(rds.smembers(self.KEY_TAGS % self.id)) if type(x) == str ]
      self._tags.sort()

    return self._tags


  def as_hash(self):
    h = super(Pin, self).as_hash()
    h['tags'] = self.tags()
    return h


  @classmethod
  def remove(cls, id):
    super(Pin, cls).remove(id)
    rds.delete(cls.KEY_TAGS % id)


class User(BaseHash):

  # link references(SET)
  # used by core.pin.new_pin to check if user has already pinned a link
  KEY_LINKS = 'fp:user:%s:links'

  # pin references(LIST)
  # used for listing a user's pins
  KEY_PINS = 'fp:user:%s:pins'

  # reverse ref (email -> user id) (HASH)
  # used by login and register check
  KEY_EMAIL_REF = 'fp:user:email:%s'

  # reverse ref (screen name -> user id) (HASH)
  # used by screen name check and user homepage
  KEY_SCREEN_NAME_REF = 'fp:user:screen_name:%s'

  # all tags that used by user (SET)
  KEY_TAGS = 'fp:user:%s:tags'

  # store pins under a tag (SET)
  KEY_TAG_PINS = 'fp:user:%s:tag:%s:pins'

  fields = {
    'email': '',
    'screen_name': '',
    'password_digest': '',
    'last_login': 0,
  }

  @classmethod
  def new(cls, email, screen_name, password_digest):
    user_id = super(User, cls).new(email=email, screen_name=screen_name, password_digest=password_digest)
    rds.set(cls.KEY_EMAIL_REF % email, user_id)
    rds.set(cls.KEY_SCREEN_NAME_REF % screen_name, user_id)

    return user_id


  @classmethod
  def get_id_by_email(cls, email):
    """
    Get user id by Email
    """
    return rds.get(cls.KEY_EMAIL_REF % email)
    

  @classmethod
  def get_id_by_screen_name(cls, screen_name):
    """
    Get user id by screen name
    """
    return rds.get(cls.KEY_SCREEN_NAME_REF % screen_name)


  def add_pin(self, pin_id):
    """
    Add pin to current user's pin list
    """
    rds.lpush(self.KEY_PINS % self.id, pin_id)


  def remove_pin(self, pin_id):
    """
    Remove pin from current user's pin list
    """
    rds.lrem(self.KEY_PINS % self.id, 1, pin_id)


  def pins(self, start=None, end=None):
    """
    Get [start..end) of the user's pins
    """
    if start is None or end is None:
      start = 0
      end = rds.llen(self.KEY_PINS % self.id)

    return rds.lrange(self.KEY_PINS % self.id, start, end - 1)


  def pin_count(self):
    """
    Get pin count
    """
    return rds.llen(self.KEY_PINS % self.id)


  def add_link(self, link_id):
    """
    Add link to current user's link set
    """
    rds.sadd(self.KEY_LINKS % self.id, link_id)


  def remove_link(self, link_id):
    """
    Remove link from current user's link set
    """
    rds.srem(self.KEY_LINKS % self.id, link_id)


  def has_link(self, link_id):
    """
    Check if link_id is in current user's link set
    """
    return rds.sismember(self.KEY_LINKS % self.id, link_id)


  def tags(self, with_count=False):
    """
    Get user's tags (list)
      with_count: return (tag, count) tuple if True
    """
    if not hasattr(self, '_tags') or self._tags is None:
      self._tags = [ x.decode('utf-8') for x in list(rds.smembers(self.KEY_TAGS % self.id)) if type(x) == str ]
      self._tags.sort()

    if with_count:
      return [ (tag, rds.scard(self.KEY_TAG_PINS % (self.id, tag))) for tag in self._tags ]
    else:
      return self._tags


  def update_pin_tags(self, pin_id, add_tags=None, remove_tags=None):
    """
    Add and remove tags to specific pin
    """
    p = rds.pipeline()

    if add_tags:
      p.sadd(self.KEY_TAGS % self.id, *add_tags)
      for tag in add_tags:
        p.sadd(self.KEY_TAG_PINS % (self.id, tag), pin_id)

    if remove_tags:
      for tag in remove_tags:
        p.srem(self.KEY_TAG_PINS % (self.id, tag), pin_id)

    p.execute()

    # see if necessary to remove any tags
    empty_tags = [ tag for tag in remove_tags if rds.scard(self.KEY_TAG_PINS % (self.id, tag)) == 0 ]
    if empty_tags:
      rds.srem(self.KEY_TAGS % self.id, *empty_tags)


  def pins_in_tag(self, tag):
    """
    Find pins under tag
    return sorted pin ids
    """
    pin_ids = list(rds.smembers(self.KEY_TAG_PINS % (self.id, tag)))
    pin_ids.sort(reverse=True)

    return pin_ids


