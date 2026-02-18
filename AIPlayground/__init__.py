from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO

import eventlet
eventlet.monkey_patch()

app = Flask(__name__, static_folder="static", template_folder="templates")

socketio = SocketIO(app, cors_allowed_origins="*")
app.config['SECRET_KEY'] = 'eda3d099ac83aece683027cd3df45167'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from AIPlayground import routes