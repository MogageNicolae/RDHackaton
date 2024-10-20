from flask import Blueprint, request, make_response, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
import uuid

from controller.utils import do_fields_exist
from model import Users


class AuthController:
    def __init__(self):
        self.blueprint = Blueprint('auth_bp', __name__, url_prefix="/auth")
        self.register_routes()

    def register_routes(self):
        self.blueprint.route('/register', methods=['POST'])(self.__register)
        self.blueprint.route('/login', methods=['POST'])(self.__login)

    @staticmethod
    def __register():
        data = request.json

        if not do_fields_exist(data, ['email', 'password', 'name', 'language']):
            return 'Missing data', 400

        if Users.get_user_by_email(data['email']):
            return 'User already exists', 409

        hashed_password = generate_password_hash(data['password'])
        user_id = str(uuid.uuid4())
        access_token = create_access_token(identity={'id': user_id, 'date': str(datetime.now())},
                                           expires_delta=timedelta(hours=24))
        user = {
            'email': data['email'],
            'username': data['name'],
            'id': user_id,
            'password': hashed_password,
            'language': data['language'],
            'token': access_token,
            'refresh_token': jwt.encode({'email': data['email'], 'date': str(datetime.now())}, 'secret', algorithm='HS256'),
            'expires_in': datetime.now() + timedelta(hours=24)
        }
        Users.add_user(user)

        return jsonify({"msg": "User registered successfully"}), 201

    @staticmethod
    def __login():
        data = request.json

        if not do_fields_exist(data, ['email', 'password']):
            return 'Missing data', 400

        user = Users.get_user_by_email(data['email'])

        if not user or not check_password_hash(user['password'], data['password']):
            return 'Invalid credentials', 401

        token = create_access_token(identity={'id': user['id'], 'date': str(datetime.now())},
                                    expires_delta=timedelta(hours=24))
        Users.update_user_token(user['email'], token, datetime.now() + timedelta(hours=24))

        response = make_response(jsonify({'token': token, 'username': user['username']}))

        return response
