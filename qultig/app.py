import os

import hashids
from flask import Flask, request, jsonify, render_template, g, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from qultig import handler

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

# Add enumerate function
app.jinja_env.globals['enumerate'] = enumerate


def connect_db():
    """Connects to the specific database."""
    engine = create_engine(app.config['DATABASE_URI'], echo=False)
    Session = sessionmaker(bind=engine)
    return Session()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'database'):
        g.database = connect_db()
    return g.database


@app.route('/')
def show_entries():
    return render_template('index.html', quiz=None)


@app.route('/art', methods=['GET'])
def art():
    db = get_db()
    h = hashids.Hashids(salt=app.config['HASH_SALT'])

    try:
        decoded_tuple = h.decode(request.args['q'])
        quiz_id = int(decoded_tuple[0])
        quiz = handler.get_art_quiz(db, quiz_id)

    except (KeyError, IndexError, handler.HandlerError, ValueError):
        new_quiz = handler.build_art_quiz(db, handler.CategoryDistribution())
        return redirect(url_for('art', q=h.encode(new_quiz.id)))

    return render_template('art.html', items=quiz.items)


@app.route('/evaluate_art', methods=['POST'])
def evaluate():
    response = handler.Response(item_id=int(request.form.get('item_id')),
                                option_id=int(request.form.get('option_id')))
    db = get_db()
    feedback = handler.get_art_feedback(db, response)
    return jsonify(correct=feedback.correct, labels=feedback.labels)


if __name__ == '__main__':
    app.run()
