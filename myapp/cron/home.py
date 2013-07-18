# -*- coding: utf8 -*-

from myapp import app
from myapp.core.models import Link

def run():

  Link.generate_recent_links()


