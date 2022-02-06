from werkzeug.security import check_password_hash, generate_password_hash
from .Db import get_db


def findone(username) -> dict:
    '''
    get userprofile from DB:user by username
    table: user
    search query: username
    return: dict
'''
    db = get_db()
    userdata = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)).fetchone()
    if userdata is None:
        return None
    return userdata


def validate_user(username, password) -> bool:
    '''
    validate user identity
    table: user
    search query: username, password
    return: user_id or None
    '''
    db = get_db()

    validated = False

    password = check_password_hash(password)
    user_id = db.execute(
        'SELECT user_id FROM user WHERE username = ? AND password = ?',
        (username, password)).fetchone()
    if user_id is not None:
        validated = True

    return validated


def register(username, password) -> bool:
    '''
    register a new user
    table: user
    search query: username
    return: boolean
    '''

    db = get_db()

    isexist = findone(username)
    if isexist:
        return False
    else:
        password = generate_password_hash(password)
        db.execute(
            'INSERT INTO user (username, password) VALUES (?, ?)',
            (username, password))
        db.commit()
        return True
