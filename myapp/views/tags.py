# -*- coding: utf8 -*-

from flask import request, redirect, render_template, url_for, abort
from myapp import app
from myapp.core.user import current_user_id
from myapp.core.models import User
from myapp.utils.common import make_context

@app.route('/me/tags')
def tag_cloud():
  """
  Show my tag cloud
  """

  user_ref = User.ref(current_user_id())
  my_tags = user_ref.tags(with_count=True)

  context = make_context({
    'my_tags': my_tags,
  })

  return render_template('tags/cloud.html', **context)
