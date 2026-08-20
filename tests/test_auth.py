import pytest
from flask import g, session
from bolao.db import get_db 


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM users WHERE username = 'a' ",
        ).fetchone() is not None

# I'll use get_data(as_text=True) to get the rsponse data as string instead of bytes, because it's more pratical in case I want check messages in Portuguese.
# So I won't be using the 'b' prefix in the strings below.
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', 'Username is required.'),
    ('a', '', 'Password is required.'),
    ('test', 'test', 'already in use'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.get_data(as_text=True)


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == '/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', 'Incorrect username'),
    ('test', 'a', 'Incorrect password'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.get_data(as_text=True)


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session