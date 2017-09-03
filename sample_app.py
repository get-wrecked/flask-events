#!./venv/bin/python

import logging.config
import os
import base64

from flask import Flask, jsonify, redirect
from flask_canonical import CanonicalLogger
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

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
canonical_logger = CanonicalLogger(app)
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
        }


@app.route('/')
def main():
    items = Item.query.all()
    canonical_logger.add_sample('item.count', len(items))
    return jsonify([item.to_json() for item in items])


@app.route('/add-random', methods=['POST'])
def add_random():
    random_name = base64.urlsafe_b64encode(os.urandom(6)).decode('utf-8')
    canonical_logger.add('name', random_name)
    db.session.add(Item(name=random_name))
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
