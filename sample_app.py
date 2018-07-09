#!./venv/bin/python

import logging.config
import os
import base64

from flask import Flask, jsonify, redirect, abort, request, Blueprint
from flask_events import Events
from flask_sqlalchemy import SQLAlchemy

logging.config.dictConfig({
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        'werkzeug': {
            'level': 'WARNING',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    },
})

mod = Blueprint('main', __name__)
db = SQLAlchemy()
events = Events()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    events.init_app(app)

    app.register_blueprint(mod)

    return app


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
        }


@mod.route('/')
def main():
    items = Item.query.all()
    events.add('item.count', len(items))
    return jsonify([item.to_json() for item in items])


@mod.route('/add-random', methods=['POST'])
def add_random():
    random_name = base64.urlsafe_b64encode(os.urandom(6)).decode('utf-8')
    events.add('name', random_name)
    db.session.add(Item(name=random_name))
    db.session.commit()
    return redirect('/')


@mod.route('/abort')
def abort_503():
    abort(503)


@mod.route('/crash')
def crash():
    message = request.args.get('message', 'no message')
    raise ValueError(message)


def cli_main():
    app = create_app()
    with app.app_context():
        db.create_all()

    print('* Listening on 127.0.0.1:5000')
    app.run(use_reloader=True)


if __name__ == '__main__':
    cli_main()
