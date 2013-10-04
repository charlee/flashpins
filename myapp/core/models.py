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
import datetime
from myapp import rds 
from myapp.utils.crypt import urlhash
from myapp.utils.common import random_string


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


  @classmethod
  def seq(cls):
    """
    Get current sequence number
    """
    return rds.get(cls.KEY_INCR)

  def __repr__(self):
    keys = self.fields.keys()
    values = [getattr(self, key) for key in keys]
    values = [ x.encode('utf-8') if x is not None else None for x in values ]
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
  KEY_TAG_POOL = 'fp:link:%s:tag_pool'
  KEY_TAGS = 'fp:link:%s:tags'

  # reverse lookup from hash to link id
  GKEY_HASH_REF = 'fp:g:link:hash_ref'

  # recent 5000 links
  GKEY_RECENT_LINKS = 'fp:g:link:recent'

  fields = {
    'title': '',
    'url': '',
    'icon': '',
    'hash': '',
    'add_date': 0,
    'access_date': 0,
  }

  def local_add_date(self):
    if self.add_date:
      timestr = datetime.datetime.fromtimestamp(int(self.add_date)).strftime('%Y-%m-%d %H:%M:%S')
      return timestr
      
    else:
      return ''

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

  def accumulate_tags(self, tags):
    """
    Accumulate tags to the link's tag pool
    """

    if tags:

      # set the tag counter
      p = rds.pipeline()
      for tag in tags:
        p.zincrby(self.KEY_TAG_POOL % self.id, tag, 1)
      p.execute()

      # cache the top 5 tags
      # TODO: this should be moved into cron job
      self._tags = rds.zrange(self.KEY_TAG_POOL % self.id, 0, 5)
      p = rds.pipeline()
      p.delete(self.KEY_TAGS % self.id)
      for tag in tags:
        p.sadd(self.KEY_TAGS % self.id, tag)
      p.execute()

  @classmethod
  def get_by_hash(cls, h):
    return rds.hget(cls.GKEY_HASH_REF, h)


  def tags(self):
    """
    Get popular tags for this link
    return a list sorted by popularity
    """
    if not hasattr(self, '_tags') or self._tags is None:
      self._tags = [ x.decode('utf-8') for x in list(rds.smembers(self.KEY_TAGS % self.id)) if type(x) == str ]
    return self._tags

  @classmethod
  def new(cls, hash, **kwargs):
    link_id = super(Link, cls).new(id=None, hash=hash, **kwargs)
    rds.hset(cls.GKEY_HASH_REF, hash, link_id)
    return link_id


  @classmethod
  def remove(cls, id):
    """
    Delete a link
    """
    super(Link, cls).remove(id)

    # clear the counters
    p.delete(cls.KEY_PIN_COUNT % id, cls.KEY_VIEW_COUNT % id)


  @classmethod
  def generate_recent_links(cls):
    """
    Generate recent links.
    Run in cronjob.
    """
    max_id = int(cls.seq() or 0)
    prev_max_id = int(rds.lindex(cls.GKEY_RECENT_LINKS, 0) or 0)
    
    for link_id in range(prev_max_id + 1, max_id + 1):
      if cls.exists(link_id):
        rds.lpush(cls.GKEY_RECENT_LINKS, link_id)
    
    rds.ltrim(cls.GKEY_RECENT_LINKS, 0, 5000)

  @classmethod
  def recent_links(cls, start=0, stop=5000):
    return rds.lrange(cls.GKEY_RECENT_LINKS, start, stop) or []

      
class Pin(BaseHash):

  fields = {
    'title': '',
    'desc': '',
    'link_id': '',
    'user_id': 0,
    'add_date': 0,
    'private': 0,
    'taglist': '',       # comma (,) separated tag list
  }


  def tags(self):
    """
    return tags (list)
    """
    if self.taglist is not None:
      return sorted(filter(None, self.taglist.split(',')))
    else:
      return []

  def as_hash(self):
    h = super(Pin, self).as_hash()
    h['tags'] = self.tags()
    return h


  def local_add_date(self):
    if self.add_date:
      timestr = datetime.datetime.fromtimestamp(int(self.add_date)).strftime('%Y-%m-%d %H:%M:%S')
      return timestr
      
    else:
      return ''


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

  # persist-cookie pair key
  # this is used to store a cookie-user pairs for "Remember Me" on the login screen
  #   param: random number
  #   value: user id
  # key will expire after 3 months(=3 * 30 * 86400)
  KEY_COOKIE_PAIR = 'fp:user:cookie:%s'
  COOKIE_PAIR_EXPIRE = 3 * 30 * 86400

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


  def tags(self, with_count=True, total=None):
    """
    Get user's tags (list)
      with_count: return (tag, count) tuple if True
      total: retrieve max "total" tags
    """

    if total is None:
      total = rds.zcard(self.KEY_TAGS % self.id)

    tags = rds.zrevrange(self.KEY_TAGS % self.id, 0, total-1, withscores=True, score_cast_func=int)

    if with_count:
      tags = [ (t.decode('utf-8'), s) for t, s in tags ]
    else:
      tags = [ t.decode('utf-8') for t, s in tags ]

    return tags


  def update_pin_tags(self, pin_id, add_tags=None, remove_tags=None):
    """
    Add and remove tags to specific pin
    """
    p = rds.pipeline()

    if add_tags:
      for tag in add_tags:
        p.zincrby(self.KEY_TAGS % self.id, tag, 1)
        p.sadd(self.KEY_TAG_PINS % (self.id, tag), pin_id)

    if remove_tags:
      p.zremrangebyscore(self.KEY_TAGS % self.id, 0, 0)
      for tag in remove_tags:
        p.srem(self.KEY_TAG_PINS % (self.id, tag), pin_id)

    p.execute()


  def pins_in_tag(self, tag):
    """
    Find pins under tag
    return sorted pin ids
    """
    pin_ids = list(rds.smembers(self.KEY_TAG_PINS % (self.id, tag)))
    pin_ids.sort(reverse=True)

    return pin_ids


  @classmethod
  def get_cookie_pair(cls, digest):
    """
    Return user_id corresponding to digest
    """
    return rds.get(cls.KEY_COOKIE_PAIR % digest)

  def make_cookie_pair(self):
    """
    Generate a cookie digest-userid pair
    """
    digest = random_string(16)
    p = rds.pipeline()
    key = self.KEY_COOKIE_PAIR % digest
    p.set(key, self.id)
    p.expire(key, self.COOKIE_PAIR_EXPIRE)
    p.execute()

    return digest

  @classmethod
  def remove_cookie_pair(cls, digest):
    """
    remove cookie-userid pair
    """
    rds.delete(cls.KEY_COOKIE_PAIR % digest)


class Global(object):

  KEY_LINKS = 'fp:tags:%s:links'        # sorted set for link ids (pinned_count -> score)
  KEY_POPULAR_TAGS = 'fp:tags:popular'  # sorted set for tags


