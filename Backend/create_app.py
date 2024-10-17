import os

import torch
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(device)
model.to(device)

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
