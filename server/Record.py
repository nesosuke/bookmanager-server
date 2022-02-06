from .Db import get_db as db


def find_id(user_id, book_id) -> int:
    '''
    search record_id by username and isbn
    table: record
    return: record_id or None
    '''
    record_id = db.execute(
        'SELECT record_id FROM record WHERE user_id = ? AND book_id = ?',
        (user_id, book_id)).fetchone()

    if record_id is None:
        return None
    return record_id['record_id']


def findone(record_id) -> dict:
    '''
    get record from DB:record by record_id
    table: record
    return: dict
    '''
    record = db.execute(
        'SELECT * FROM record WHERE record_id = ?', (record_id,)).fetchone()
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
    records_raw = db.execute(
        'SELECT * FROM record WHERE user_id = ? ORDER BY record_at DESC',
        (user_id,)).fetchall()  # type: list[dict]

    if records_raw is not None:
        records = [{} for i in range(len(records_raw))]
        for i, rec_raw in enumerate(records_raw):
            records[i]['record_id'] = rec_raw['record_id']
            records[i]['isbn'] = rec_raw['isbn']
            records[i]['title'] = rec_raw['title']
            records[i]['author'] = rec_raw['author']
            records[i]['publisher'] = rec_raw['publisher']
            records[i]['status'] = rec_raw['status']
            records[i]['rating'] = rec_raw['rating']
            records[i]['comment'] = rec_raw['comment']
            records[i]['record_at'] = rec_raw['record_at'].isoformat()
    return records


def upsert(
    user_id, book_id, status, record_id=None, rating=None, comment=None
) -> dict:
    '''
    UPSERT record to DB:record
    table: record
    insert query: user_id, book_id, status, rating, comment
    update query: status, rating, comment
    return: updated record
    '''
    record_id = find_id(user_id, book_id)

    # If record exist, update record
    if record_id is not None:
        db.execute(
            'UPDATE record SET status = ?, rating = ?, comment = ? \
                WHERE record_id = ?',
            (status, rating, comment, record_id))
        db.commit()
        return findone(record_id)

    # If record not exist, insert record
    else:
        db.execute(
            'INSERT INTO record (user_id, book_id, status, rating, comment) \
                VALUES (?, ?, ?, ?, ?)',
            (user_id, book_id, status, rating, comment))
        db.commit()
        return findone(db.lastrowid)


def delete(record_id):
    '''
    delete record from DB:record
    table: record
    '''
    response = db.execute(
        'DELETE FROM record WHERE record_id = ?', (record_id,))
    db.commit()
    return response
