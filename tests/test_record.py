import pytest
from server.db import get_db


def test_index(client, auth):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data


@pytest.mark.parametrize('path', (
    '/record',
    '/record/detail/1',
    '/record/detail/1/edit',
    '/record/detail/1/delete',
))
def test_login_required(client, path):
    response = client.get(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'


def test_record_list(client, auth):
    auth.login()
    response = client.get('/record/')
    assert b'<h1>Records</h1>' in response.data


def test_record_add(client, auth):
    auth.login()
    response = client.post(
        '/record/9784873119328'
    )
    assert response.headers['Location'] == 'http://localhost/record'
    assert b'<h1>New Record</h1>' in response.data
    assert b'Title' in response.data
    assert b'Author' in response.data
    assert b'9784873119328' in response.data
    assert b'type="radio" name="status" value="read" checked>' in response.data
    assert b'type="radio" name="status" value="unread">' in response.data
    assert b'type="radio" name="status" value="reading">' in response.data
    assert b'type="radio" name="status" value="will_read">' in response.data
    assert b'type="radio" name="status" value="wont_read">' in response.data
    assert b'type="radio" name="status" value="cancelled">' in response.data
    assert b'<textarea name="comment">' in response.data
    assert b'<input type="submit" value=>' in response.data


def test_record_detail(client, auth):
    auth.login()
    response = client.get('/record/detail/1')
    assert b'2022-01-01 00:00:00' in response.data


def test_record_detail_edit(client, auth):
    auth.login()
    response = client.get('/record/detail/1/edit')
    assert b'href=Edit' in response.data


def test_record_detail_delete(client, auth):
    auth.login()
    response = client.get('/record/detail/1/delete')
    assert b'href=Delete' in response.data


def test_record_detail_tried_to_edit_by_irregular_user(client, auth, app):
    with app.app_context():
        db = get_db()
        db.execute('UPDATE record SET user_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    assert client.get('/record/detail/1/edit').status_code == 403
    assert client.get('/record/detail/1/delete').status_code == 403
    assert b'href="/record/detail/1/edit"' not in client.get(
        '/record/detail/1').data
    assert b'href="/record/detail/1/delete"' not in client.get(
        '/record/detail/1').data

    assert client.get('/record/detail/1').status_code == 200


@pytest.mark.parametrize('path', (
    '/record/detail/2',
    '/record/detail/2/edit',
    '/record/detail/2/delete',
))
def test_exists_record(client, auth, path):
    auth.login()
    assert client.get(path).status_code == 404
