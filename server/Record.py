from server import User
from . import Book
from .Db import get_db


def validate_status(status) -> bool:
    valid_status = ['read', 'unread', 'reading',
                    'will_read', 'wont_read', 'cancelled']
    return status in valid_status


def validate_rating(rating) -> bool:
    valid_rating = [None, 1, 2, 3, 4, 5]
    return rating in valid_rating


def find_id(user_id, book_id) -> int:
    '''
    search record_id by username and isbn
    table: record
    return: record_id or None
    '''

    db = get_db()

    record_id = db.execute(
        'SELECT id FROM record WHERE user_id = ? AND book_id = ?',
        (user_id, book_id)).fetchone()

    if record_id is None:
        return None
    return record_id['id']


def getid(username, isbn) -> int:
    '''
    get record_id by username and isbn
    table: record
    return: record_id or None
    '''

    db = get_db()

    user = User.findone(username=username)
    if user is None:
        return None
    else:
        user_id = user['id']

    book = Book.findone(isbn=isbn)
    if book is None:
        return None
    else:
        book_id = book['id']

    record_id = db.execute(
        'SELECT id FROM record WHERE user_id = ? AND book_id = ?',
        (user_id, book_id)).fetchone()

    if record_id is None:
        return None
    return record_id['id']


def findone(record_id: int) -> dict:
    '''
    get record from DB:record by record_id
    table: record
    return: dict
    '''

    db = get_db()

    record = db.execute(
        'SELECT * FROM record WHERE id = ?', (record_id,)).fetchone()
    if record is None:
        return None
    record = dict(record)

    record['record_id'] = record['id']

    username = User.findone(id=record['user_id'])['username']
    isbn = Book.findone(id=record['book_id'])['isbn']

    bookinfo = Book.findone(isbn)

    record['isbn'] = isbn
    record['username'] = username
    record['title'] = bookinfo['title']
    record['author'] = bookinfo['author']
    record['publisher'] = bookinfo['publisher']
    record['record_at'] = record['record_at'].isoformat()

    return record


def findall(user_id) -> list:
    '''
    get all records from DB:record by user_id
    table: record
    search query: user_id
    post-process: get bookinfo from DB:book by book_id
              and add bookinfo to each record
    return: list of dict, sorted by record_at DESC
'''

    db = get_db()

    records_raw = db.execute(
        'SELECT * FROM record WHERE user_id = ? ORDER BY record_at DESC',
        (user_id,)).fetchall()
    records_raw = list(records_raw)

    username = User.findone(id=user_id)['username']

    if records_raw is not None:
        records = [{} for i in range(len(records_raw))]
        for i, rec_raw in enumerate(records_raw):
            records[i]['record_id'] = rec_raw['id']
            records[i]['status'] = rec_raw['status']
            records[i]['rating'] = rec_raw['rating']
            records[i]['comment'] = rec_raw['comment']
            records[i]['record_at'] = rec_raw['record_at'].isoformat()

            bookinfo = Book.findone(id=rec_raw['book_id'])
            records[i]['isbn'] = bookinfo['isbn']
            records[i]['title'] = bookinfo['title']
            records[i]['author'] = bookinfo['author']
            records[i]['publisher'] = bookinfo['publisher']

            records[i]['username'] = username
    return records


def upsert(
    user_id, book_id, status, rating=None, comment=None
) -> dict:
    '''
    UPSERT record to DB:record
    table: record
    insert query: user_id, book_id, status, rating, comment
    update query: status, rating, comment
    return: updated record
    '''

    db = get_db()

    record_id = find_id(user_id, book_id)

    # validate input
    if not validate_status(status) or not validate_rating(rating):
        return None

    # If record exist, update record
    if record_id is not None:
        db.execute(
            'UPDATE record SET (status, rating, comment) \
                = (?, ?, ?) WHERE id = ?',
            (status, rating, comment, record_id))
        db.commit()
        record = findone(record_id)
        return dict(record)

    # If record not exist, insert record
    else:
        db.execute(
            'INSERT INTO record (user_id, book_id, status, rating, comment) \
                VALUES (?, ?, ?, ?, ?)',
            (user_id, book_id, status, rating, comment))
        db.commit()
        record_id = find_id(user_id, book_id)
        record = findone(record_id)
        return dict(record)


def delete(record_id) -> bool:
    '''
    delete record from DB:record
    table: record
    '''

    db = get_db()

    db.execute(
        'DELETE FROM record WHERE id = ?', (record_id,))
    db.commit()
    return True
