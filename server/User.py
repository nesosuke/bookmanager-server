from werkzeug.security import check_password_hash, generate_password_hash
from .Db import get_db


def findone(username=None, id=None) -> dict:
    '''
    get user from DB:user by username
    table: user
    search query: username
    return: dict
'''
    db = get_db()
    if username is not None:
        userdata = db.execute(
            'SELECT * FROM user WHERE username = ? ', (username,)).fetchone()
    if id is not None:
        userdata = db.execute(
            'SELECT * FROM user WHERE id = ? ', (id,)).fetchone()
    if userdata is None:
        return None
    return userdata


def available(username: str) -> bool:
    '''
    check if username is preserved
    table: user
    query: username
    return: boolean
    '''

    preserved_usernames = ['admin', 'guest', 'root', 'administrator']
    if username in preserved_usernames:
        return False

    isexist = findone(username)
    if isexist:
        return False
    else:
        return True


def validate_user(username, password) -> bool:
    '''
    validate user identity
    table: user
    search query: username, password
    return: user_id or None
    '''
    db = get_db()

    validated = False

    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)).fetchone()

    if user is None:
        validated = False
        return validated

    if check_password_hash(user['password'], password):
        validated = True

    return validated


def register(username, password) -> bool:
    '''
    register a new user
    table: user
    query: username
    return: boolean
    '''

    db = get_db()

    if available(username) is False:
        return False
    else:
        password = generate_password_hash(password)
        db.execute(
            'INSERT INTO user (username, password) VALUES (?, ?)',
            (username, password))
        db.commit()
        return True


def delete(username, password) -> bool:
    '''
    delete a user
    table: user
    query: username, password, confirm
    return: boolean
    '''

    db = get_db()

    if validate_user(username, password) is False:
        return False
    else:
        db.execute(
            'DELETE FROM user WHERE username = ?', (username,))
        db.commit()
        return True
