import pytest

# show book info
# no login required
# endpoint: /book
# method: GET
# params: isbn
# return: json

endpoint = '/book/'


@pytest.mark.parametrize(('isbn', 'message'), (
    # book not found
    ('9784873119329', (404),),
    # book found
    ('9784873119328', (200)),
))
# when user is not logged in, return only book info
def test_get_bookinfo_by_isbn(client, isbn, message):
    response = client.get(endpoint + isbn)
    assert response.status_code == message[0]
    assert '入門Python 3' in response.data.decode('utf-8')


# @pytest.mark.parametrize(('isbn', 'user_id', 'message'), (
#     # book not found, user found
#     ('9784873119329', 1, (404, None)),
#     # book not found, user not found
#     ('9784873119329', 2, (404, None)),
#     # book found, user found
#     ('9784873119328', 1, (200, None)),
# ))
# # when user is logged in AND when already recorded, redirect to record page
# def test_get_bookinfo_by_isbn_when_logged_in(client, auth, isbn, message):
#     auth.login()

#     response = client.get(endpoint + isbn)
#     assert response.status_code == message[0]
#     assert '入門Python 3' in response.data.decode('utf-8')
