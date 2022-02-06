from flask import Blueprint, abort, jsonify, request

from . import Book, Record, User

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
    book = Book.findone(isbn)
    if book is None:
        abort(404)
    return jsonify(book)


@bp.route('/user/<username>/records')
def getall_records(username) -> object:
    '''
    Show all records of a user
    '''
    user = User.findone(username)
    if user is None:
        abort(404)
    user_id = user['id']
    records = Record.findall(user_id)
    return jsonify(records)


# Handle User

@bp.route('/user/register', methods=['POST'])
def register() -> object:
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

    result = User.register(username, password)
    if result is False:
        abort(409)
    else:
        return jsonify({'message': 'Register Successfully'})


@bp.route('/user/delete', methods=['POST'])
def delete() -> object:
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

    if User.delete(username, password) is False:
        abort(400)
    else:
        return jsonify({'message': 'Delete Successfully'})
# Handle Record


@bp.route('record/<record_id>')
def getone_record(record_id) -> object:
    '''
    Return a record
    '''
    record = Record.findone(record_id)
    if record is None:
        abort(404)
    return jsonify(record)


@bp.route('/record/update', methods=['POST'])
def upsert_record() -> object:
    '''
    Upsert a record
    Required parameters: username, password, isbn, status
    Optional parameters: record_id, rating, comment
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

    record_id = data['record_id'] if 'record_id' in data else None
    rating = data['rating'] if 'rating' in data else None
    comment = data['comment'] if 'comment' in data else None

    if User.validate_user(username, password) is False:
        abort(401)

    if Book.findone(isbn) is None:
        abort(404)

    record = Record.upsert(username, isbn, status, record_id, rating, comment)
    return jsonify(record)


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

    if User.validate_user(username, password) is False:
        abort(401)

    if Record.findone(record_id) is None:
        abort(404)

    record = Record.delete(record_id)
    return jsonify(record)
