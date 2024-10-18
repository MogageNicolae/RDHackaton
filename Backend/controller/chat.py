import ast
import json
import os
import re
import subprocess
import uuid
import openai
import torch
import torchaudio
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from controller.utils import do_fields_exist, map_language_to_m2m, map_language_to_seamless
from create_app import tokenizer, translation_model, processor, multilingual_model
from model import Chats, Messages, Users


class ChatController:
    def __init__(self, app):
        self.blueprint = Blueprint('chat_bp', __name__, url_prefix='/chat')
        self.register_routes()
        self.app = app
        openai.api_key = self.app.config['OPENAI_API_KEY']

    def register_routes(self):
        self.blueprint.route('/create', methods=['POST'])(self.__create_chat)
        self.blueprint.route('/delete', methods=['DELETE'])(self.__delete_chat)
        self.blueprint.route('/send_message/text', methods=['POST'])(self.__send_message_text)
        self.blueprint.route('/send_message/audio', methods=['POST'])(self.__send_message_audio)
        self.blueprint.route('/<chat_id>', methods=['GET'])(self.__get_messages)
        self.blueprint.route('/history', methods=['GET'])(self.__get_chat_history)

    @jwt_required()
    def __create_chat(self):
        data = request.json

        if not do_fields_exist(data, ['user1', 'user2']):
            return 'Missing data', 400

        chat = {
            'user1': data['user1'],
            'user2': data['user2'],
            'chat_id': str(uuid.uuid4()),
        }
        Chats.add_chat_room(chat)

        return jsonify(chat['chat_id'])

    @jwt_required()
    def __delete_chat(self):
        chat_id = request.args.get('chat_id')

        Chats.delete_chat_room(chat_id)

        return 'chat deleted'

    @jwt_required()
    def __send_message_text(self):
        data = request.json

        if not do_fields_exist(data, ['chat_id', 'sender', 'message']):
            return 'Missing data', 400

        chat = Chats.get_chat_room_by_id(data['chat_id'])
        if not chat:
            return 'chat not found', 404

        user1 = Users.get_user_by_username(chat['user1'])[0]
        user2 = Users.get_user_by_username(chat['user2'])[0]

        message, translated_message = self.__translate_message(data, chat, user1, user2)

        message = {
            'chat_id': data['chat_id'],
            'sender': data['sender'],
            'type': 'text',
            'message_user1': message,
            'message_user2': translated_message,
            'date': datetime.now()
        }
        Messages.add_message(message)

        return 'message sent'

    def convert_webm_to_wav(self, input_path, output_path):
        command = f"ffmpeg -i {input_path} -c:a pcm_f32le {output_path}"
        subprocess.run(command, shell=True, check=True)

    def count_files_in_directory(self, directory):
        return len([file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))])

    @jwt_required()
    def __send_message_audio(self):
        if 'file' not in request.files:
            return 'No file part', 401
        if 'chat_id' not in request.form or 'sender' not in request.form:
            return 'Missing data', 400

        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400

        chat = Chats.get_chat_room_by_id(request.form['chat_id'])
        if not chat:
            return 'chat not found', 404

        user1_path, user2_path = self.__create_paths(chat)

        temp_webm_path = os.path.join(user1_path, file.filename)
        audio_count = self.count_files_in_directory(user1_path)
        file.filename = f"{audio_count}.wav"
        temp_wav_path = os.path.join(user1_path, file.filename)
        file.save(temp_webm_path)

        try:
            self.convert_webm_to_wav(temp_webm_path, temp_wav_path)
            os.remove(temp_webm_path)
        except subprocess.CalledProcessError as e:
            print(f"Error during conversion: {e}")
            return 'File conversion failed', 500

        file_path_user1, file_path_user2 = self.__translate_audio(file, user1_path, user2_path, chat)

        message = {
            'chat_id': request.form['chat_id'],
            'sender': request.form['sender'],
            'type': 'audio',
            'message_user1': file_path_user1,
            'message_user2': file_path_user2,
            'date': datetime.now()
        }
        Messages.add_message(message)

        print(jsonify(file.filename))
        return jsonify(file.filename)

    def __create_paths(self, chat):
        chat_folder_path = os.path.join(self.app.config['AUDIO_UPLOAD_FOLDER'], chat['chat_id'])
        user1_path = os.path.join(chat_folder_path, chat['user1'])
        user2_path = os.path.join(chat_folder_path, chat['user2'])

        if not os.path.exists(chat_folder_path):
            os.makedirs(user1_path, exist_ok=True)
            os.makedirs(user2_path, exist_ok=True)

        return user1_path, user2_path

    @staticmethod
    def __create_audio_files(file, user1_path, user2_path, tgt_lang):
        file_path_user1 = os.path.join(user1_path, file.filename)
        # file.save(file_path_user1)
        file_path_user2 = os.path.join(user2_path, file.filename)

        audio, orig_freq = torchaudio.load(file_path_user1, format="wav")
        audio = torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=16_000)
        audio_inputs = processor(audios=audio, return_tensors="pt").to(multilingual_model.device)
        audio_array_from_audio = multilingual_model.generate(**audio_inputs, tgt_lang=tgt_lang)[0].cpu().numpy()
        torchaudio.save(file_path_user2, torch.tensor(audio_array_from_audio), 16_000)

        return file_path_user1, file_path_user2

    def __translate_message(self, data, chat, user1, user2):
        if data['sender'] == chat['user1']:
            src_lang = map_language_to_m2m(user1['language'])
            tgt_lang = map_language_to_m2m(user2['language'])
            message = data['message']
            translated_message = self.translate_text(data['message'], src_lang, tgt_lang)
        else:
            src_lang = map_language_to_m2m(user2['language'])
            tgt_lang = map_language_to_m2m(user1['language'])
            translated_message = data['message']
            message = self.translate_text(data['message'], src_lang, tgt_lang)
        return message, translated_message

    def __translate_audio(self, file, user1_path, user2_path, chat):
        user1 = Users.get_user_by_username(chat['user1'])[0]
        user2 = Users.get_user_by_username(chat['user2'])[0]

        if user1['username'] == request.form['sender']:
            tgt_lang = map_language_to_seamless(user2['language'])
            file_path_user1, file_path_user2 = self.__create_audio_files(file, user1_path, user2_path, tgt_lang)
        else:
            tgt_lang = map_language_to_seamless(user1['language'])
            file_path_user2, file_path_user1 = self.__create_audio_files(file, user2_path, user1_path, tgt_lang)

        return file_path_user1, file_path_user2

    @jwt_required()
    def __get_messages(self, chat_id):
        page = int(request.args.get('page', 1))
        sender = request.args.get('sender')

        messages = Messages.get_messages_by_chat_id(chat_id, page)

        return_messages = []

        chat = Chats.get_chat_room_by_id(chat_id)

        for message in messages:
            if sender == chat['user1']:
                message_to_append = message['message_user1']
            else:
                message_to_append = message['message_user2']

            if message['type'] == 'audio':
                print(message_to_append)
                print(message_to_append.split("\\")[-1])
                message_to_append = message_to_append.split("\\")[-1]

            return_messages.append({
                'sender': message['sender'],
                'message': message_to_append,
                'type': message['type'],
                'date': message['date']
            })

        return jsonify(return_messages)

    @jwt_required()
    def __get_chat_history(self):
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

    def translate_text(self, text, src_lang, tgt_lang):
        tokenizer.src_lang = src_lang
        sentences = self.split_text(text)
        translated_sentences = []
        for sentence in sentences:
            if sentence:
                if re.match(r'^[a-zA-Z0-9 ,\']*[.!?]*$', sentence):
                    translated_sentences.append(self.translate_sentence(sentence, tgt_lang))
                else:
                    translated_sentences.append(sentence)
        return ' '.join(translated_sentences)

    @staticmethod
    def translate_sentence(sub_sentence, tgt_lang):
        encoded = tokenizer(sub_sentence, return_tensors="pt").to(translation_model.device)
        generated_tokens = translation_model.generate(encoded['input_ids'], forced_bos_token_id=tokenizer.get_lang_id(tgt_lang))
        translation = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        return translation

    @staticmethod
    def split_text(text):
        prompt = f"Split the following text into an array where the text are in separate values so a translation model \
                    can translate it good, emojis and symbols not being affected. \
                    For example '🤡 Esti bine?? =))' should be ['🤡', 'Esti bine??', '=))']:\n\n{text}"

        chat_completion = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that splits text into an array of sentences "
                                              "based only on the . ? ! keys. Do not split based on commas or apostrophe. "
                                              "You only respond with the split array."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        response = json.loads(chat_completion.model_dump_json(indent=2))
        splitted_text = ast.literal_eval(response['choices'][0]['message']['content'])
        return splitted_text
