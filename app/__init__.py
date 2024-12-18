from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap4
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap4()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    return app
