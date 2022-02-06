# /api tests
import pytest
import json
import time

# /api access


def test_api_top(client):
    response = client.get('/api/')
    assert response.status_code == 200


# get book information by isbn
# endpoint: /api/book/<isbn>
# method: GET
# required params: isbn
# return: json


@pytest.mark.parametrize(('isbn', 'message'), (
    # book  found
    ('9784873119328',
        (200,
         {'isbn': '9784873119328',
          'title': '入門Python 3',
          'author': 'Lubanovic, Bill',
          'publisher': 'オライリー・ジャパン',
          'year': None,
          'edition': '第2版',
          'genre': None,
          'series': '',
          'volume': '',
          'description': None,
          'permalink': 'https://iss.ndl.go.jp/books/R100000074-I000721538-00',
          'ndl_image_url': None})),
    # book not found
    ('9784873119329',
     (404, None),
     )))
def test_get_bookinfo_by_isbn(client, isbn, message):
    response = client.get('/api/book/' + isbn)
    assert response.status_code == message[0]
    assert response.json == message[1]


# get a record by record_id
# endpoint: /api/record/<record_id>
# method: GET
# required params: record_id
# return: json
@pytest.mark.parametrize(('record_id', 'message'), (
    # record found
    ('1',
        (200, {'record_id': 1,
               'isbn': '9784873119328',
               'title': '入門Python 3',
               'author': 'Lubanovic, Bill',
               'publisher': 'オライリー・ジャパン',
               'username': 'test',
               'status': 'read',
               'rating': 5,
               'comment': 'test comment',
               'record_at': '2022-01-01T00:00:00'})),
    # record not found
    ('2',
     (404, None),
     ))
)
def test_get_a_record_by_record_id(client, record_id, message):
    response = client.get('/api/record/' + record_id)
    assert response.status_code == message[0]
    if response.status_code == 200:
        assert response.json == message[1]


# get all records of a user by username
# endpoint: /api/user/<username>/records
# method: GET
# required params: user_id
# return: json
@pytest.mark.parametrize(('username', 'message'), (
    # user not found
    ('wrong_user',
        (404, None),
     ),
    # user found, but no record
    ('other',
        (200, []),
     ),
    # user found
    ('test',
        (200, [{'record_id': 1,
                'username': 'test',
                'isbn': '9784873119328',
                'title': '入門Python 3',
                'author': 'Lubanovic, Bill',
                'publisher': 'オライリー・ジャパン',
                'status': 'read',
                'rating': 5,
                'comment': 'test comment',
                'record_at': '2022-01-01T00:00:00'}])),

))
def test_get_all_records_of_a_user(client, username, message):
    response = client.get('/api/user/' + username + '/records')
    assert response.status_code == message[0]
    assert response.json == message[1]


# upsert a record
# endpoint: /api/record/update
# method: POST
# required params: username, isbn, status
# optional params: rating, comment
# return: response with record_id OR error message


@pytest.mark.parametrize(('username', 'password', 'isbn', 'status',
                          'rating', 'comment', 'message'), (
    # invliad authentication -> return 401
    ('wrong_user', 'wrong_password', '9784873119328', 'read', 1, 'test', (
        401, {'message': 'Unauthorized'})),
    # valid authentication, valid input -> return 200, record_id,
    ('test', 'test', '9784873113937', 'read', 1, 'test',  (
        200, {
            "record_id": 2,
            "title": "初めてのPython",
            "status": "read",
            "username": "test",
            "isbn": "9784873113937",
            "author": 'Lutz, Mark',
            "publisher": 'オライリー・ジャパン',
            "rating": 1,
            "comment": "test",
            "record_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        })),
    # valid authentication, invalid input -> return 400, error message
    ('test', 'test', '9784873119328', '', 1, 'test', (
        400, {'message': 'Bad Request'})),
    # valid authentication, valid input, but book not found -> return 404
    ('test', 'test', '9784873119329', 'read', 1, 'test', (
        404, {'message': 'Not Found'})),
))
def test_api_post_a_record(client, username, password, isbn,
                           status, rating, comment, message):
    response = client.post(
        '/api/record/update',
        data=json.dumps({'username': username,
                         'password': password,
                         'isbn': isbn,
                         'status': status,
                         'rating': rating,
                         'comment': comment}),
        content_type='application/json')

    assert response.status_code == message[0]
    if response.status_code == 200:
        assert response.json == message[1]
