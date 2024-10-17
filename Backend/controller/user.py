from flask import Blueprint

user_bp = Blueprint('user_bp', __name__)


@user_bp.route('/userinfo', methods=['GET'])
def userinfo():
    return 'User info'
