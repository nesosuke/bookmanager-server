import pytest

# show anything only if logged in
# endpoint: /record


# when not logged in, should be redirected to login page
@pytest.mark.parametrize(('path'), (
    '/record',
    '/record/detail/1',
    '/record/detail/1/update',
    '/record/detail/1/delete',
    '/record/new',

))
def test_when_not_logged_in(client, path):
    response = client.get(path)
    print(response.status_code)
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/auth/login'


# when already logged in, should be shown records page


def test_when_logged_in(client, auth, path):
    auth.login()
    response = client.get(path)
    assert response.status_code == 200
    assert b'<h1>Records</h1>' in response.data
    assert b'{{ user["username"] }}' in response.data
