from conftest import login


def test_registration_uses_hub_account_and_starts_session(client):
    credentials = {'username': 'new.family', 'password': 'good-password'}
    response = client.post('/api/auth/register', json=credentials)
    assert response.status_code == 201, response.text
    assert response.json()['username'] == 'new.family'
    assert 'access_token' not in response.json()
    assert 'HttpOnly' in response.headers['set-cookie']
    assert client.get('/api/auth/me').json()['username'] == 'new.family'
    assert client.post('/api/auth/logout').status_code == 200
    assert client.post('/api/auth/register', json=credentials).status_code == 409
    assert client.post('/api/auth/login', json=credentials).status_code == 200
    assert client.get('/api/auth/me').json()['username'] == 'new.family'


def test_registration_validation_and_csrf(client):
    credentials = {'username': 'another', 'password': 'good-password'}
    assert client.post('/api/auth/register', headers={'Origin': 'https://evil.example'}, json=credentials).status_code == 403
    for password in ['short', 'é' * 37]:
        credentials['password'] = password
        assert client.post('/api/auth/register', json=credentials).status_code == 422
    credentials.update(username='bad name', password='good-password')
    assert client.post('/api/auth/register', json=credentials).status_code == 422
