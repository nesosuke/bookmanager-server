# /web tests

import pytest
import json

#   test /web access


def test_web_top(client):
    response = client.get('/web/')
    assert response.status_code == 200
    assert b'<title>' in response.data

# test /web/book/<isbn>


@pytest.mark.parametrize(('isbn', 'message'), (
    # book found
    ('9784873119328',
        {
            200,
            {
                b'9784873119328',
                b'Python 3',
                b'Lubanovic, Bill',
                b'オライリー・ジャパン',
            }
        }
     ),
    # book not found
    ('9784873119329',
        {200,
            {
                b'Not found'
            }
         }
     )))
def test_web_book_detail(client, isbn, message):
    response = client.get('/web/book/' + isbn)
    assert response.status_code == message[0]
    assert response.data == message[1]


# test /web/record/<record_id>
@pytest.mark.parametrize(('record_id', 'message'), (
    # record found
    ('1',
        {
            200,
            {
                b'9784873119328',
                b'Python 3',
                b'Lubanovic, Bill',
                b'オライリー・ジャパン',
                b'test',
                b'read',
                b'5',
                b'test comment',
                b'2022-01-01T00:00:00'
            }
        }
     ),
    ('2',
        {
            200,
            {
                b'Not found'
            }
        })))
def test_web_record_detail(client, record_id, message):
    response = client.get('/web/record/' + record_id)
    assert response.status_code == message[0]
    assert response.data == message[1]

# test /web/record/new


@pytest.mark.parametrize(('message'), (
    {
        200,
        {
            b'Record create',
            b'submit'}
    }))
def test_web_record_new(client,message):
    response = client.get('/web/record/new')
    assert response.status_code == message[0]
    assert response.data == message[1]
