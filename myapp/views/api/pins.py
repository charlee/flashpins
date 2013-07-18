# -*- coding: utf8 -*-

from myapp import app
from flask import Blueprint, request, jsonify, abort, make_response
from flask.ext.csrf import csrf_exempt
from myapp.core.user import j_require_login, current_user_id
from myapp.core.pin import new_pin, remove_pin, update_pin
from myapp.core.models import Pin, Link

api_pins = Blueprint('api_pins', __name__)

@api_pins.route('/<int:pin_id>', methods=['GET'])
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


@api_pins.route('/<int:pin_id>', methods=['PATCH'])
def pin_update(pin_id):

  if not request.json:
    abort(400)

  p = request.json
  params = dict([(k, p.get(k)) for k in ['title', 'desc', 'private'] if k in p])
  if 'tags' in p:
    params['tags'] = filter(None, p.get('tags').split(','))

  update_pin(pin_id=pin_id, **params)

  return jsonify({ 'id': pin_id })


@csrf_exempt
@api_pins.route('/', methods=['POST'])
@j_require_login()
def pin_create():
  if not request.json or not request.json.get('url'):
    abort(400)

  p = request.json

  pin_id = new_pin(url=p.get('url'),
                   user_id=current_user_id(),
                   title=p.get('title'),
                   desc=p.get('desc'),
                   tags=filter(None, p.get('tags').split(',')),
                   private=p.get('private'))

  if pin_id:
    return make_response(jsonify({ 'id': pin_id }), 200)

  else:
    abort(409)


@api_pins.route('/<int:pin_id>', methods=['DELETE'])
def pin_destroy(pin_id):

  remove_pin(pin_id)

  return ''

