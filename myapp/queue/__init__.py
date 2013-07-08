from pickle import loads, dumps
from myapp import app, rds
from uuid import uuid4

_shared_tasks = {}

class DelayedResult(object):
  def __init__(self, key):
    self.key = key
    self._rv = None

  @property
  def return_value(self):
    if self._rv is None:
      rv = rds.get(self.key)
      if rv is not None:
        self._rv = loads(rv)
    return self._rv

  @property
  def ready(self):
    return rds.exists(self.key)


def task(f):

  # key for shared tasks dict
  skey = '%s:%s' % (f.__module__, f.__name__)


  def delay(*args, **kwargs):
    qkey = app.config['REDIS_QUEUE_KEY']
    key = '%s:result:%s' % (qkey, str(uuid4()))
    s = dumps((skey, key, args, kwargs))
    rds.rpush(qkey, s)
    return DelayedResult(key)
    

  f.delay = delay

  _shared_tasks[skey] = f

  return f

def queue_daemon(app, rv_ttl=500, daemon=False):

  
  while 1:
    msg = rds.blpop(app.config['REDIS_QUEUE_KEY'])
    skey, key, args, kwargs = loads(msg[1])
    func = _shared_tasks.get(skey, None)

    if func:

      print "Run %s.." % func.__name__

      try:
        rv = func(*args, **kwargs)
      except Exception, e:
        rv = e
      if rv is not None:
        rds.setex(key, rv_ttl, dumps(rv))

    else:
      print "Unable to find function %s" % skey

from queue import tasks

