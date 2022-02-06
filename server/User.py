from flask import check_password_hash
from .Db import get_db as db


def findone(username) -> dict:
    '''
    get userprofile from DB:user by username
    table: user
    search query: username
    return: dict
'''
    userdata = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)).fetchnone()
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
    validated = False

    password = check_password_hash(password)
    user_id = db.execute(
        'SELECT user_id FROM user WHERE username = ? AND password = ?',
        (username, password)).fetchone()
    if user_id is not None:
        validated = True

    return validated
