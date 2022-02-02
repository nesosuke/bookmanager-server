from flask import (
    Flask, Blueprint, abort, jsonify, request,)
from server.db import get_db
from werkzeug.security import check_password_hash

bp = Blueprint('api', __name__, url_prefix='/api')

status_list = ['read', 'unread', 'reading',
               'will_read', 'wont_read', 'cancelled']

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
    return jsonify(response)


# /user/<username>/records, return records of a user
@bp.route('/user/<username>/records')
def get_all_records_of_a_user(username):
    db = get_db()
    user = db.execute(
        'SELECT id FROM user WHERE username = ?', (username,)
    ).fetchone()
    if user is None:
        abort(404)
    # if True: # for debug
    #     return {'message': 'Fxxx'}
    records = db.execute(
        'SELECT * FROM record WHERE user_id = ?', (user['id'],)
    ).fetchall()
    if records is None:
        return jsonify([])
    records = [dict(record) for record in records]
    response = [{} for i in range(len(records))]
    for i, record in enumerate(records):
        book = db.execute(
            'SELECT isbn,title,author,publisher FROM book WHERE id = ?',
            (record['book_id'],)).fetchone()
        response[i]['record_id'] = record['id']
        response[i]['username'] = username
        response[i]['isbn'] = book['isbn']
        response[i]['title'] = book['title']
        response[i]['author'] = book['author']
        response[i]['publisher'] = book['publisher']
        response[i]['status'] = record['status']
        response[i]['rating'] = record['rating']
        response[i]['comment'] = record['comment']
        response[i]['record_at'] = record['record_at'].isoformat()

        del record['id'], record['user_id'], record['book_id']
    return jsonify(response)


# post a record
# endpoint: /record/new
# required parameters: username, password, isbn, status
# optional parameters: rating, comment
# return: record_id OR error
@bp.route('/record/new', methods=('POST', 'GET'))
def post_a_new_record():
    if request.method == 'GET':
        abort(405)

    # get parameters from data
    username = request.json['username']
    password = request.json['password']
    isbn = request.json['isbn']
    status = request.json['status']
    rating = request.json.get('rating', None)
    comment = request.json.get('comment', None)

    # validate parameters
    if username == '' or password == '' or isbn == '' or \
            status not in status_list:
        abort(400)
    db = get_db()
    user = None
    user = db.execute(
        'SELECT id, password FROM user WHERE username = ?', (
            username,)).fetchone()
    if user is None:
        abort(401)

    if check_password_hash(user['password'], password) is False:
        abort(401)

    # validate isbn
    book = db.execute(
        'SELECT * FROM book WHERE isbn = ?', (isbn,)
    ).fetchone()

    # book not found
    if book is None:
        abort(404)

    # check duplicate record
    record = db.execute(
        'SELECT * FROM record WHERE user_id = ? AND book_id = ?',
        (user['id'], book['id'])).fetchone()

    if record is not None:
        abort(409)

    # insert record
    db.execute(
        'INSERT INTO record (user_id, book_id, status, rating, comment) \
            VALUES (?, ?, ?, ?, ?)',
        (user['id'], book['id'], status, rating, comment))
    db.commit()
    result = db.execute(
        'SELECT id, record_at FROM record WHERE (user_id,book_id)=(?,?)',
        (user['id'], book['id'])).fetchone()
    result = dict(result)
    if result is None:
        abort(500)

    response = {'result': 'success',
                'record': {
                    'record_id': result['id'],
                    'title': book['title'],
                    'status': status}}

    return jsonify(response)
