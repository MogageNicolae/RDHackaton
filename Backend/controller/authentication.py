from flask import Blueprint, request, make_response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
import uuid

from controller.utils import does_fields_exist
from model import Users

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    if not does_fields_exist(data, ['email', 'password', 'name', 'language']):
        return 'Missing data', 400

    if Users.get_user_by_email(data['email']):
        return 'User already exists', 409

    hashed_password = generate_password_hash(data['password'])
    user = {
        'email': data['email'],
        'username': data['name'],
        'id': str(uuid.uuid4()),
        'password': hashed_password,
        'language': data['language'],
        'token': jwt.encode({'id': 'id', 'date': str(datetime.now())}, 'secret', algorithm='HS256'),
        'refresh_token': jwt.encode({'email': data['email']}, 'secret', algorithm='HS256'),
        'expires_in': datetime.now() + timedelta(hours=24)
    }
    Users.add_user(user)

    return jsonify({"msg": "User registered successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    if not does_fields_exist(data, ['email', 'password']):
        return 'Missing data', 400

    user = Users.get_user_by_email(data['email'])

    if not user or not check_password_hash(user['password'], data['password']):
        return 'Invalid credentials', 401

    token = jwt.encode({'id': user['id'], 'date': str(datetime.now())}, 'secret', algorithm='HS256')
    Users.update_user_token(user['email'], token, datetime.now() + timedelta(hours=24))

    response = make_response(jsonify({'token': token, 'username': user['username']}))

    return response
