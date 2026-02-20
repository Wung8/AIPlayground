from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from flask_login import LoginManager

import eventlet
eventlet.monkey_patch()

import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__, static_folder="static", template_folder="templates")

socketio = SocketIO(app, cors_allowed_origins="*", log_output=False)
app.config['SECRET_KEY'] = 'eda3d099ac83aece683027cd3df45167'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from backend import routes