import os
import torch
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer, AutoProcessor, SeamlessM4Tv2Model

translation_model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
multilingual_model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large")
# processor = None
# multilingual_model = None

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(device)
translation_model.to(device)
multilingual_model.to(device)

mongo = PyMongo()
jwt = JWTManager()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
    app.config['AUDIO_UPLOAD_FOLDER'] = os.environ.get('AUDIO_UPLOAD_FOLDER')
    app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['JWT_ALGORITHM'] = os.environ.get('JWT_ALGORITHM')
    CORS(app, supports_credentials=True, resources={
        r"/*": {
            "origins": ["http://localhost:3000"]
        }
    })

    mongo.init_app(app)
    jwt.init_app(app)

    from controller import AuthController, ChatController, UserController, MessageController, AssetsController
    app.register_blueprint(AuthController().blueprint)
    app.register_blueprint(UserController().blueprint)
    app.register_blueprint(ChatController(app).blueprint)
    app.register_blueprint(MessageController(app).blueprint)
    app.register_blueprint(AssetsController().blueprint)

    return app
