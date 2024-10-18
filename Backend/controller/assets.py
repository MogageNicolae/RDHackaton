import os

from flask import Blueprint, send_file
from flask_jwt_extended import jwt_required


class AssetsController:
    def __init__(self):
        self.blueprint = Blueprint('assets_bp', __name__, url_prefix='/assets')
        self.register_routes()

    def register_routes(self):
        self.blueprint.route('/audio/<chat_id>/<username>/<file_name>', methods=['GET'])(self.__get_asset)

    def __get_asset(self, chat_id, username, file_name):
        file_path = f'./assets/audios/{chat_id}/{username}/{file_name}'

        print(file_path)
        if not os.path.exists(file_path):
            return 'File not found', 404

        return send_file(file_path)
