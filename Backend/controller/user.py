from flask import Blueprint, jsonify

from model import Users

user_bp = Blueprint('user_bp', __name__, url_prefix="/user")


@user_bp.route('/<username>', methods=['GET'])
def get_username(username):
    users = Users.get_user_by_username(username)

    return_users = []

    for user in users:
        return_users.append({
            'username': user['username'],
            'email': user['email']
        })

    return jsonify(return_users)
