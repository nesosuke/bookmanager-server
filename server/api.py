from flask import Blueprint, abort, jsonify, request

from . import book, record, user

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/')
def index() -> str:  # TODO: edit response message
    response = "Hello, World!"
    return response

# Handle Book


@bp.route('/book/<isbn>')
def get_bookinfo(isbn) -> object:
    '''
    Return book info
    '''
    bookdata = book.findone(isbn)
    if bookdata is None:
        abort(404)

    del bookdata['id']
    return jsonify(bookdata)


# Handle User

@bp.route('/user/register', methods=['POST'])
def register_user() -> object:
    '''
    Register a new user
    '''
    data = dict(request.json)
    try:
        username = data['username']
        password = data['password']
        confirm = data['confirm']
    except KeyError:
        abort(400)
    if confirm != 'Yes':
        abort(400)

    result = user.register(username, password)
    if result is False:
        abort(409)
    else:
        return jsonify({'message': 'Register Successfully'})


@bp.route('/user/delete', methods=['POST'])
def delete_user() -> object:
    '''
    Delete exist user
    '''

    data = dict(request.json)
    try:
        username = data['username']
        password = data['password']
        confirm = data['confirm']
    except KeyError:
        abort(400)

    if confirm != 'Yes':
        abort(400)

    if user.delete(username, password) is False:
        abort(400)
    else:
        return jsonify({'message': 'Delete Successfully'})
# Handle Record


@bp.route('record/<record_id>')
def getone_record(record_id) -> object:
    '''
    Return a record
    '''
    recorddata = record.findone(record_id)
    if recorddata is None:
        abort(404)

    del recorddata['id'], recorddata['user_id'], recorddata['book_id']
    return jsonify(recorddata)


@bp.route('/user/<username>/records')
def getall_records(username) -> object:
    '''
    Show all records of a user
    '''
    userdata = user.findone(username)
    if userdata is None:
        abort(404)
    user_id = userdata['id']
    records = record.findall(user_id)
    return jsonify(records)


@bp.route('/record/update', methods=['POST'])
def upsert_record() -> object:
    '''
    Upsert a record
    Required parameters: username, password, isbn, status
    Optional parameters: rating, comment
    Method: POST
    Data Format: JSON
    Return: upserted record
    '''
    data = dict(request.json)

    try:
        username = data['username']
        password = data['password']
        isbn = data['isbn']
        status = data['status']
    except KeyError:
        abort(400)

    rating = data['rating'] if 'rating' in data else None
    comment = data['comment'] if 'comment' in data else None

    if user.validate_user(username, password) is False:
        abort(401)

    userdata = user.findone(username=username)
    bookdata = book.findone(isbn=isbn)
    if userdata is None or bookdata is None:
        abort(404)

    user_id = userdata['id']
    book_id = bookdata['id']
    recorddata = record.upsert(user_id=user_id, book_id=book_id,
                           status=status, rating=rating, comment=comment)
    if recorddata is None:
        abort(400)

    result = {}
    result = {'record_id': recorddata['id'],
              'username': username,
              'isbn': isbn,
              'title': bookdata['title'],
              'author': bookdata['author'],
              'status': status,
              'publisher': bookdata['publisher'],
              'rating': rating,
              'comment': comment,
              'record_at': recorddata['record_at']}

    return jsonify(result)


@bp.route('/record/delete', methods=['POST'])
def delete_record() -> object:
    '''
    Delete a record
    Required parameters: username, password, record_id
    Method: POST
    Data Format: JSON
    '''
    data = dict(request.json)
    try:
        username = data['username']
        password = data['password']
        record_id = data['record_id']
    except KeyError:
        abort(400)

    if user.validate_user(username, password) is False:
        abort(401)

    if record.findone(record_id) is None:
        abort(404)

    recorddata = record.delete(record_id)
    return jsonify(recorddata)
