import io

from PIL import Image
from sqlalchemy import select, func
from app.core import database as db, config
from conftest import login


def test_startup_preserves_existing_recipes_and_parts(client):
    before = client.get('/api/recipes/48').json()
    with db.session() as session:
        count = session.scalar(select(func.count()).select_from(db.Recipe))
    db.init_database()
    with db.session() as session:
        assert session.scalar(select(func.count()).select_from(db.Recipe)) == count
    assert client.get('/api/recipes/48').json() == before
    assert before['parts'][0]['title'] == 'Pizzateig'


def test_default_public_auth_and_ownership(client, payload):
    assert client.post('/api/recipes/', json=payload).status_code == 401
    assert client.delete('/recipes/48').status_code == 401
    login(client)
    result = client.post('/api/recipes/', json=payload)
    assert result.status_code == 201, result.text
    recipe = result.json()
    assert recipe['id'] > 88 and recipe['is_public'] is True
    assert recipe['owner_id'] == 1001 and len(recipe['parts']) == 1
    login(client, 'bob')
    assert client.get(f"/api/recipes/{recipe['id']}").status_code == 200
    assert client.put(f"/api/recipes/{recipe['id']}", json=payload).status_code == 403
    assert client.delete(f"/api/recipes/{recipe['id']}").status_code == 403
    assert client.put('/api/recipes/48', json=payload).status_code == 403
    assert client.post('/tags/', json={'name': 'evil'}).status_code == 405
    login(client)
    assert client.delete(f"/api/recipes/{recipe['id']}").status_code == 200


def test_private_recipe_part_image_and_tags_are_hidden(client, payload):
    login(client)
    payload['is_public'] = False
    payload['tags'] = ['OnlyAliceCanSeeThis']
    recipe = client.post('/api/recipes/', json=payload).json()
    rid = recipe['id']
    part_id = recipe['parts'][0]['id']
    raw = io.BytesIO()
    Image.new('RGB', (3000, 2000), 'red').save(raw, 'PNG')
    assert client.post(f'/api/recipes/{rid}/image', files={'image': ('test.png', raw.getvalue(), 'image/png')}).status_code == 200
    assert client.get(f'/api/recipes/{rid}/image').status_code == 200
    for user in ('bob', None):
        if user: login(client, user)
        else: client.post('/api/auth/logout')
        assert rid not in [r['id'] for r in client.get('/api/recipes/').json()]
        for endpoint in (f'/api/recipes/{rid}', f'/recipes/{rid}', f'/api/recipes/{part_id}', f'/api/recipes/{rid}/image'):
            response = client.get(endpoint)
            assert response.status_code == 404
            assert response.headers['cache-control'] == 'private, no-store'
        assert 'OnlyAliceCanSeeThis' not in str(client.get('/api/tags/').json())
    login(client)
    assert client.get(f'/api/recipes/{rid}').status_code == 200
    payload['is_public'] = True
    response = client.put(f'/api/recipes/{rid}', json=payload)
    assert response.status_code == 200, response.text
    client.post('/api/auth/logout')
    assert client.get(f'/api/recipes/{rid}').status_code == 200
    login(client)
    payload['is_public'] = False
    assert client.put(f'/api/recipes/{rid}', json=payload).status_code == 200
    client.post('/api/auth/logout')
    assert client.get(f'/api/recipes/{rid}/image').status_code == 404
    login(client)
    assert client.delete(f'/api/recipes/{rid}').status_code == 200
    assert client.get(f'/api/recipes/{part_id}').status_code == 404
    with db.session() as session:
        assert not session.scalar(select(db.Ingredient.id).where(db.Ingredient.recipe_id == part_id))


def test_image_resizes_strips_metadata_and_rejects_invalid_uploads(client, payload, monkeypatch):
    login(client)
    rid = client.post('/api/recipes/', json=payload).json()['id']
    raw = io.BytesIO()
    exif = Image.Exif()
    exif[270] = 'private metadata'
    Image.new('RGB', (3600, 2400), 'blue').save(raw, 'JPEG', exif=exif)
    result = client.post(f'/api/recipes/{rid}/image', files={'image': ('big.jpg', raw.getvalue(), 'image/jpeg')})
    assert result.status_code == 200
    response = client.get(f'/api/recipes/{rid}/image')
    resized = Image.open(io.BytesIO(response.content))
    assert max(resized.size) == 1600 and resized.format == 'JPEG'
    assert not resized.getexif() and len(response.content) < len(raw.getvalue())
    assert response.headers['cache-control'] == 'private, no-store'
    assert client.post(f'/api/recipes/{rid}/image', files={'image': ('evil.svg', b'<svg/>', 'image/jpeg')}).status_code == 400
    monkeypatch.setattr(config, 'MAX_IMAGE_BYTES', 100)
    assert client.post(f'/api/recipes/{rid}/image', files={'image': ('big.jpg', b'x'*101, 'image/jpeg')}).status_code == 413
    assert client.delete(f'/api/recipes/{rid}/image').status_code == 200
    assert client.get(f'/api/recipes/{rid}/image').status_code == 404
    client.delete(f'/api/recipes/{rid}')


def test_csrf_login_cookie_and_payload_validation(client, payload):
    assert client.post('/api/auth/login', headers={'Origin': 'https://evil.example'}, json={'username': 'alice', 'password': 'correct'}).status_code == 403
    response = client.post('/api/auth/login', json={'username': 'alice', 'password': 'correct'})
    assert 'HttpOnly' in response.headers['set-cookie'] and 'SameSite=lax' in response.headers['set-cookie']
    assert 'access_token' not in response.json()
    assert client.get('/api/auth/me').json()['username'] == 'alice'
    payload['owner_id'] = 1002
    assert client.post('/api/recipes/', json=payload).status_code == 422
    payload.pop('owner_id')
    payload['parent_id'] = 48
    assert client.post('/api/recipes/', json=payload).status_code == 422
    payload.pop('parent_id')
    payload['title'] = '  '
    assert client.post('/api/recipes/', json=payload).status_code == 422
    client.post('/api/auth/logout')
    assert client.get('/api/auth/me').json() is None


def test_original_image_and_revoked_session(client):
    response = client.get('/api/recipes/48/image')
    assert response.status_code == 200
    client.cookies.set(config.COOKIE_NAME, 'revoked', path='/api')
    assert client.get('/api/auth/me').json() is None
    assert client.delete('/api/recipes/48').status_code == 401
