import json
import os
import uuid
from datetime import datetime
import openai
from flask import Blueprint, request, jsonify

from controller.utils import does_fields_exist
# from create_app import processor, model
from model import Chats, Messages, Users

chat_bp = Blueprint('chat_bp', __name__, url_prefix='/chat')

openai.api_key = os.environ.get('OPENAI_API_KEY')


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


@chat_bp.route('/history', methods=['GET'])
def get_chat_history():
    username = request.args.get('username')

    chats = Chats.get_chat_rooms_by_user_id(username)

    return_chats = []

    for chat in chats:
        return_chats.append({
            'chat_id': chat['chat_id'],
            'user1': chat['user1'],
            'user2': chat['user2']
        })

    return jsonify(return_chats)


def translate_text(text, target_language="English"):
    prompt = f"Translate the following text to {target_language}:\n\n{text}"

    chat_completion = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that translates text."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    response = json.loads(chat_completion.model_dump_json(indent=2))
    translated_text = response['choices'][0]['message']['content']
    return translated_text

# def translate_text(text, src_lang="ron", tgt_lang="eng"):
#     text_inputs = processor(text=text, src_lang=src_lang, return_tensors="pt").to(model.device)
#
#     output_tokens = model.generate(**text_inputs, tgt_lang=tgt_lang, generate_speech=False)
#     translated_text_from_text = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)
#     return translated_text_from_text


