import os
from io import BytesIO

import torch
import torchaudio
from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required

from controller.utils import do_fields_exist, map_language_to_seamless
from create_app import processor, multilingual_model
from model import Chats, Users


class MessageController:
    def __init__(self, app):
        self.blueprint = Blueprint('message_bp', __name__, url_prefix='/message')
        self.register_routes()
        self.app = app

    def register_routes(self):
        self.blueprint.route('/audio/transcribe', methods=['GET'])(self.__transcribe_audio)
        self.blueprint.route('/text/to-audio', methods=['GET'])(self.__text_to_audio)

    @jwt_required()
    def __transcribe_audio(self):
        chat_id = request.args.get('chat_id')
        sender = request.args.get('sender')
        audio_file = request.args.get('audio_file')

        chat = Chats.get_chat_room_by_id(chat_id)
        if not chat:
            return 'Chat not found', 404

        if chat['user1'] == sender:
            user = 'user1'
            language = Users.get_user_by_username(chat['user2'])[0]['language']
            tgt_lang = map_language_to_seamless(language)
        else:
            user = 'user2'
            language = Users.get_user_by_username(chat['user1'])[0]['language']
            tgt_lang = map_language_to_seamless(language)

        audio, orig_freq = torchaudio.load(os.path.join(self.app.config['AUDIO_UPLOAD_FOLDER'], chat_id, user, audio_file))
        audio = torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=16_000)
        audio_inputs = processor(audios=audio, return_tensors="pt").to(multilingual_model.device)
        output_tokens = multilingual_model.generate(**audio_inputs, tgt_lang=tgt_lang, generate_speech=False)
        translated_text_from_audio = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)

        return translated_text_from_audio


    @jwt_required()
    def __text_to_audio(self):
        data = request.json

        if not do_fields_exist(data, ['text', 'username']):
            return 'Missing data', 400

        language = Users.get_user_by_username(data['username'])[0]['language']
        mapped_language = map_language_to_seamless(language)

        text_inputs = processor(text=data['text'], src_lang=language, return_tensors="pt").to(multilingual_model.device)
        audio_array_from_text = multilingual_model.generate(**text_inputs, tgt_lang=mapped_language)[0].cpu().numpy().squeeze()

        audio_tensor = torch.tensor(audio_array_from_text).unsqueeze(0)
        buf = BytesIO()
        torchaudio.save(buf, audio_tensor, 16_000, format="wav")
        buf.seek(0)

        return send_file(buf, mimetype='audio/wav', as_attachment=True, download_name='output.wav')
