from .Db import get_db

valid_status = ['read', 'unread', 'reading',
                'will_read', 'wont_read', 'cancelled']
valid_rating = [1, 2, 3, 4, 5]


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


def findone(record_id) -> dict:
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
        (user_id,)).fetchall()  # type: list[dict]

    if records_raw is not None:
        records = [{} for i in range(len(records_raw))]
        for i, rec_raw in enumerate(records_raw):
            records[i]['record_id'] = rec_raw['id']
            records[i]['book_id'] = rec_raw['book_id']

            # records[i]['title'] = rec_raw['title']
            # records[i]['author'] = rec_raw['author']
            # records[i]['publisher'] = rec_raw['publisher']
            records[i]['status'] = rec_raw['status']
            records[i]['rating'] = rec_raw['rating']
            records[i]['comment'] = rec_raw['comment']
            records[i]['record_at'] = rec_raw['record_at'].isoformat()
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

    # validate status and rating
    if status not in valid_status or rating not in valid_rating:
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
