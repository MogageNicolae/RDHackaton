import os

from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

mongo = PyMongo()
jwt = JWTManager()


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
    CORS(app, supports_credentials=True)

    mongo.init_app(app)
    jwt.init_app(app)

    from controller import auth_bp, chat_bp, user_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(user_bp)

    return app
