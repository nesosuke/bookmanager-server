from . import user
from . import book
from .db import get_db


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

    userdata = user.findone(username=username)
    if userdata is None:
        return None
    else:
        user_id = userdata['id']

    bookdata = book.findone(isbn=isbn)
    if bookdata is None:
        return None
    else:
        book_id = bookdata['id']

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

    recorddata = db.execute(
        'SELECT * FROM record WHERE id = ?', (record_id,)).fetchone()
    if recorddata is None:
        return None
    recorddata = dict(recorddata)

    recorddata['record_id'] = recorddata['id']

    username = user.findone(id=recorddata['user_id'])['username']
    isbn = book.findone(id=recorddata['book_id'])['isbn']

    bookdata = book.findone(isbn)

    recorddata['isbn'] = isbn
    recorddata['username'] = username
    recorddata['title'] = bookdata['title']
    recorddata['author'] = bookdata['author']
    recorddata['publisher'] = bookdata['publisher']
    recorddata['record_at'] = recorddata['record_at'].isoformat()

    return recorddata


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

    username = user.findone(id=user_id)['username']

    if records_raw is not None:
        records = [{} for i in range(len(records_raw))]
        for i, rec_raw in enumerate(records_raw):
            records[i]['record_id'] = rec_raw['id']
            records[i]['status'] = rec_raw['status']
            records[i]['rating'] = rec_raw['rating']
            records[i]['comment'] = rec_raw['comment']
            records[i]['record_at'] = rec_raw['record_at'].isoformat()

            bookinfo = book.findone(id=rec_raw['book_id'])
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
        recorddata = findone(record_id)
        return dict(recorddata)

    # If record not exist, insert record
    else:
        db.execute(
            'INSERT INTO record (user_id, book_id, status, rating, comment) \
                VALUES (?, ?, ?, ?, ?)',
            (user_id, book_id, status, rating, comment))
        db.commit()
        record_id = find_id(user_id, book_id)
        recorddata = findone(record_id)
        return dict(recorddata)


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
