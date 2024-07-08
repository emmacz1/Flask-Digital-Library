from functools import wraps
import secrets
from flask import request, jsonify
import decimal
from json import JSONEncoder

from app.models import User

def token_required(our_flask_function):
    @wraps(our_flask_function)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        if not token:
            return jsonify({'message': 'Token is missing.'}), 401

        current_user_token = User.query.filter_by(token=token).first()
        if not current_user_token:
            return jsonify({'message': 'Token is invalid'}), 401

        return our_flask_function(current_user_token, *args, **kwargs)

    return decorated

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return super().default(obj)

custom_json_encoder = CustomJSONEncoder()
