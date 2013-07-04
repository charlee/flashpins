from myapp import app
from flask import request, jsonify, abort, make_response
from core.user import j_require_login
from core.pin import new_pin, remove_pin, update_pin
from core.models import Pin, Link

@app.route('/j/pins/<int:pin_id>', methods=['GET'])
def pin_show(pin_id):
  pin = Pin.get(pin_id)
  if not pin:
    abort(404)

  link = Link.get(pin.link_id)

  if not pin.title:
    pin.title = link.title

  result = pin.as_hash()
  result['link'] = link.as_hash()

  return jsonify(result)


@app.route('/j/pins/<int:pin_id>', methods=['PATCH'])
def pin_update(pin_id):

  if not request.json:
    abort(400)

  p = request.json
  params = dict([(k, p.get(k)) for k in ['title', 'desc', 'tags', 'private'] if k in p])
  update_pin(pin_id=pin_id, **params)

  return jsonify({ 'id': pin_id })


@app.route('/j/pins/', methods=['POST'])
@j_require_login()
def pin_create():
  if not request.json or not pin.get('url'):
    abort(400)

  p = request.json

  pin_id = new_pin(url=p.get('url'),
                   user_id=current_user_id(),
                   title=p.get('title'),
                   desc=p.get('desc'),
                   tags=p.get('tags'),
                   private=p.get('private'))

  if pin_id:
    return make_response(jsonify({ 'id': pin_id }), 201)

  else:
    abort(409)


@app.route('/j/pins/<int:pin_id>', methods=['DELETE'])
def pin_destroy(pin_id):

  remove_pin(pin_id)

  return make_response('', 204)

