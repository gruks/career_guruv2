from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from career.config import Config
from flask_cors import CORS
from dotenv import load_dotenv
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()

# Load environment variables from .env
load_dotenv()

# Fetch keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SERPAPI_KEY1 = os.getenv("SERPAPI_KEY1")

def create_app(config_class=Config):
    app = Flask(__name__, static_url_path="/")
    app.config.from_object(config_class)

    # Init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Register blueprints
    from career.users.routes import users
    from career.main.routes import main
    app.register_blueprint(users)
    app.register_blueprint(main)

    # Enable CORS for all routes or specific routes
    CORS(app, resources={r"/data": {"origins": "http://127.0.0.1:5000"}})

    return app