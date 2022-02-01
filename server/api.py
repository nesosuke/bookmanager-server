from flask import (
    Flask, Blueprint, render_template, Response, abort)
from server.auth import login_required
from server.db import get_db
import json

bp = Blueprint('api', __name__, url_prefix='/api')

# /api, return  response 200


@bp.route('/')
def index():
    response = "Hello, World!"
    return response

# /book/<isbn>, return bookinfo


@bp.route('/book/<isbn>')
def get_bookinfo(isbn):
    db = get_db()
    book = db.execute(
        'SELECT * FROM book WHERE isbn = ?', (isbn,)
    ).fetchone()
    if book is None:
        abort(404)
    response = dict(book)
    del response['id']
    return response

# /record/<record_id>, return recordinfo


@bp.route('/record/<record_id>')
def get_recordinfo(record_id):
    db = get_db()
    record = db.execute(
        'SELECT * FROM record WHERE id = ?', (record_id,)
    ).fetchone()
    if record is None:
        abort(404)

    response = dict(record)
    response['record_id'] = record['id']
    response['record_at'] = record['record_at'].isoformat()
    response['username'] = db.execute(
        'SELECT username FROM user WHERE id = ?', (record['user_id'],)
    ).fetchone()['username']
    book = db.execute(
        'SELECT isbn,title,author,publisher FROM book WHERE id = ?',
        (record['book_id'],)).fetchone()
    response['isbn'] = book['isbn']
    response['title'] = book['title']
    response['author'] = book['author']
    response['publisher'] = book['publisher']
    del response['id'], response['user_id'], response['book_id']
    return response


# /user/<username>/records, return records of a user
@bp.route('/user/<username>/records')  # FIXME
def get_all_records_of_a_user(username):
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()
    if user is None:
        abort(404)

    if True:
        return "FUCK"

    records = db.execute(
        'SELECT * FROM record WHERE user_id = ?', (user['id'],)
    ).fetchall()
    records = [dict(record) for record in records]
    response = [{} for i in range(len(records))]
    for i, record in enumerate(records):
        response[i]['record_id'] = record['id']
        response[i]['record_at'] = record['record_at'].isoformat()
        response[i]['username'] = username
        book = db.execute(
            'SELECT isbn,title,author,publisher FROM book WHERE id = ?',
            (record['book_id'],)).fetchone()
        response[i]['isbn'] = book['isbn']
        response[i]['title'] = book['title']
        response[i]['author'] = book['author']
        response[i]['publisher'] = book['publisher']
        del record['id'], record['user_id'], record['book_id']
    print(response)
    return json.dumps(response)
