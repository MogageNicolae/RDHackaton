import uuid
from datetime import datetime

from flask import Blueprint, request, jsonify

from create_app import processor, model
from model import Chats, Messages, Users

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
    page = int(request.args.get('page', 1))

    messages = Messages.get_messages_by_chat_id(chat_id, page)

    return_messages = []

    chat = Chats.get_chat_room_by_id(chat_id)
    user1 = Users.get_user_by_id(chat['user1'])
    user2 = Users.get_user_by_id(chat['user2'])

    # src_lang = user1['language']
    # tgt_lang = user2['language']

    for message in messages:
        if message['sender'] == chat['user1']:
            message_to_append = message['message']
        else:
            message_to_append = translate_text(message['message']) #, src_lang, tgt_lang)

        return_messages.append({
            'sender': message['sender'],
            'message': message_to_append,
            'date': message['date']
        })

    return jsonify(return_messages)


def translate_text(text, src_lang="ron", tgt_lang="eng"):
    text_inputs = processor(text=text, src_lang=src_lang, return_tensors="pt").to(model.device)

    output_tokens = model.generate(**text_inputs, tgt_lang=tgt_lang, generate_speech=False)
    translated_text_from_text = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)
    return translated_text_from_text


def does_fields_exist(data, fields):
    for field in fields:
        if field not in data:
            return False
    return True
