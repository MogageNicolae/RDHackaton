from flask import Blueprint, jsonify

from model import Users


class UserController:
    def __init__(self):
        self.blueprint = Blueprint('user_bp', __name__, url_prefix="/user")
        self.register_routes()

    def register_routes(self):
        self.blueprint.route('/<username>', methods=['GET'])(self.__get_username)

    @staticmethod
    def __get_username(username):
        users = Users.get_user_by_username(username)

        return_users = []

        for user in users:
            return_users.append({
                'username': user['username'],
                'email': user['email']
            })

        return jsonify(return_users)
