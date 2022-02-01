# /api tests
import pytest
import json


# /api access
def test_api_top(client):
    response = client.get('/api/')
    assert response.status_code == 200


# fetch book information by isbn
# endpoint: /api/book/<isbn>
# method: GET
# params: isbn
# return: json


@pytest.mark.parametrize(('isbn', 'response'), (
    # book  found
    ('9784873119328',
        (200,
         {'isbn': '9784873119328',
          'title': '入門Python 3',
          'author': 'Lubanovic, Bill',
          'publisher': 'オライリー・ジャパン', })),
    # book not found
    ('9784873119329',
     (404, {'message': 'Book not found.'}),
     )))
def test_fetch_bookinfo_by_isbn(client, isbn, response):
    response = client.get('/api/book/' + isbn)
    assert response.status_code == response[0]
    assert response.json == response[1]


# fetch a record by record_id
# endpoint: /api/record/<record_id>
# method: GET
# params: record_id
# return: json
@pytest.mark.parametrize(('record_id', 'response'), (
    # record found
    ('1',
        (200, {'record_id': '1',
               'isbn': '9784873119328',
               'title': '入門Python 3',
               'author': 'Lubanovic, Bill',
               'publisher': 'オライリー・ジャパン',
               'username': 'test',
               'status': 'read',
               'rating': '5',
               'comment': 'test comment',
               'record_at': '20222-01-01T00:00:00'})),
    # record not found
    ('2',
     (404, {'message': 'Record not found.'}),
     ))
)
def test_fetch_a_record_by_record_id(client, record_id, response):
    response = client.get('/api/record/' + record_id)
    assert response.status_code == response[0]
    assert response.json == response[1]


# fetch all records of a user by username
# endpoint: /api/user/<username>/records
# method: GET
# params: user_id
# return: json
@pytest.mark.parametrize(('username', 'response'), (
    # user not found
    ('wrong_user',
        (404, {'message': 'User not found.'}),
     ),
    # user found
    ('test',
        (200, [{'record_id': '1',
                'isbn': '9784873119328',
                'title': '入門Python 3',
                'author': 'Lubanovic, Bill',
                'publisher': 'オライリー・ジャパン',
                'status': 'read',
                'rating': '5',
                'comment': 'test comment',
                'record_at': '20222-01-01T00:00:00'}])),
    # user found, but no record
    ('other',
        (200, []),
     ),
))
def test_fetch_all_records_of_a_user_by_username(client, username, response):
    response = client.get('/api/user/' + username + '/records')
    assert response.status_code == response[0]
    assert response.json == response[1]


# post a record
# endpoint: /api/record/new
# required login
# method: POST
# params: isbn, status, comment
# return: response with record_id OR error message


@pytest.mark.parametrize(('username', 'password', 'isbn', 'status', 'comment', 'response'), (
    # invliad authentication -> return 401
    ('wrong_user', 'wrong_password', '9784873119328', 'read', 'test', (
        401, 'application/json', '{"result":"failed","message":"Unauthorized"}')),
    # valid authentication, valid input -> return 200, record_id,
    ('test', 'test', '9784873113937', 'read', 'test',  (
        201, 'application/json', '{"result":"success","record_id":1}')),
    # valid authentication, invalid input -> return 400, error message
    ('test', 'test', '9784873119328', '', 'test', (
        400, 'application/json', '{"result":"failed","message":"Bad Request"}')),
    # valid authentication, valid input, but record already exists -> return 409, error message
    ('test', 'test', '9784873119328', 'read', 'test', (
        409, 'application/json', '{"result":"failed","message":"Conflict"}')),
))
def test_api_post_a_record(client, username, password, isbn, status, comment, response):
    response = client.post(
        '/api/record/new',
        data=json.dumps({'username': username, 'password': password,
                         'isbn': isbn, 'status': status, 'comment': comment}),
        content_type='application/json',
    )
    assert response.status_code == response[0]
    assert response.content_type == response[1]
    assert response.data == response[2]


# update a record
# endpoint: /api/record/<record_id>/update
# required login
# method: POST
# params: isbn,status,comment
# return: response with record_id and updated record OR error message

@pytest.mark.parametrize(('username', 'password', 'record_id', 'isbn', 'status', 'comment', 'response'), (
    # invliad authentication -> return 401
    ('wrong_user', 'wrong_password', '1', '9784873119328', 'read', 'test', (
        401, 'application/json', '{"result":"failed","message":"Unauthorized"}')),
    # valid authentication, valid input -> return 200, record_id and updated record
    ('test', 'test', '1', '9784873119328', 'read', 'test',  (
        200, 'application/json', '{"result":"success","record_id":1,"record":{"record_id":1,"username":"test","title":"test","author":"test","isbn":"9784873119328","status":"read","comment":"test","rating":0,"record_at":"2022-01-01T00:00:00"}}')),
    # valid authentication, invalid input -> return 400, error message
    ('test', 'test', '1', '9784873119328', '', 'test', (
        400, 'application/json', '{"result":"failed","message":"Bad Request"}')),
    # valid authentication, valid input, but record not exists -> return 404, error message
    ('test', 'test', '2', '9784873119328', 'read', 'test', (
        404, 'application/json', '{"result":"failed","message":"Not Found"}')),
))
def test_api_update_a_record(client, username, password, record_id, isbn, status, comment, response):
    response = client.post(
        '/api/record/' + record_id + '/update',
        data=json.dumps({'username': username, 'password': password,
                         'isbn': isbn, 'status': status, 'comment': comment}),
        content_type='application/json',
    )
    assert response.status_code == response[0]
    assert response.content_type == response[1]
    assert response.data == response[2]
