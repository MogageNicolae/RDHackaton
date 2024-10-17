from flask import Blueprint

chat_bp = Blueprint('chat_bp', __name__, url_prefix='/chat')


@chat_bp.route('/create', methods=['GET'])
def create_chat():
    return 'chat created'


@chat_bp.route('/delete', methods=['GET'])
def delete_chat():
    return 'chat deleted'


@chat_bp.route('/send_message', methods=['GET'])
def send_message():
    return 'message sent'


@chat_bp.route('/get_messages', methods=['GET'])
def get_messages():
    return 'messages retrieved'
