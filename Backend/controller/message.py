from flask import Blueprint


class MessageController:
    def __init__(self):
        self.blueprint = Blueprint('message_bp', __name__, url_prefix='/message')
        self.register_routes()

    def register_routes(self):
        self.blueprint.route('/audio/transcribe', methods=['POST'])(self.__transcribe_audio)
        self.blueprint.route('/text/to-audio', methods=['GET'])(self.__text_to_audio)

    @staticmethod
    def __transcribe_audio():
        return 'transcribe audio'

    @staticmethod
    def __text_to_audio():
        return 'text to audio'
