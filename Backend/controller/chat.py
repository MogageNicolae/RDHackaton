import uuid
from datetime import datetime

from flask import Blueprint, request, jsonify

from model import Chats, Messages

chat_bp = Blueprint('chat_bp', __name__, url_prefix='/chat')


@chat_bp.route('/create', methods=['POST'])
def create_chat():
    data = request.json

    if not does_fields_exist(data, ['user1', 'user2']):
        return 'Missing data', 400

    chat = {
        'user1': data['user1'],
        'user2': data['user2'],
        'chat_id': str(uuid.uuid4()),
    }
    Chats.add_chat_room(chat)

    return chat['chat_id']


@chat_bp.route('/delete', methods=['DELETE'])
def delete_chat():
    chat_id = request.args.get('chat_id')

    Chats.delete_chat_room(chat_id)

    return 'chat deleted'


@chat_bp.route('/send_message', methods=['POST'])
def send_message():
    data = request.json

    if not does_fields_exist(data, ['chat_id', 'sender', 'message']):
        return 'Missing data', 400

    message = {
        'chat_id': data['chat_id'],
        'sender': data['sender'],
        'message': data['message'],
        'date': datetime.now()
    }

    print(data)
    chat = Chats.get_chat_room_by_id(data['chat_id'])
    print(chat)
    if not chat:
        return 'chat not found', 404

    Messages.add_message(message)

    return 'message sent'


@chat_bp.route('/<chat_id>', methods=['GET'])
def get_messages(chat_id):
    messages = Messages.get_messages_by_chat_id(chat_id)

    return_messages = []

    for message in messages:
        return_messages.append({
            'sender': message['sender'],
            'message': message['message'],
            'date': message['date']
        })

    return jsonify(return_messages)


def does_fields_exist(data, fields):
    for field in fields:
        if field not in data:
            return False
    return True
