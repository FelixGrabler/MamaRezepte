import os
import sys
import tempfile
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
workspace = Path(tempfile.mkdtemp(prefix="mamarezepte-tests-"))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{workspace}/test.db")
os.environ["IMAGE_DIR"] = str(BACKEND / 'images')
os.environ["UPLOAD_DIR"] = str(workspace / 'uploads')
os.environ["COOKIE_SECURE"] = "false"
os.environ["SITE_ORIGIN"] = "http://testserver"

from fastapi.testclient import TestClient
from app.main import app
from app.core import auth, database, config


@pytest.fixture(autouse=True)
def mock_hub(monkeypatch):
    import httpx
    accounts = {name: (id, "correct") for name, id in {"alice": 1001, "bob": 1002, "felix": 1003}.items()}
    def request(method, path, **kwargs):
        token = kwargs.get('headers', {}).get('Authorization', '').removeprefix('Bearer ')
        if path.endswith('/register'):
            credentials = kwargs['json']
            name = credentials['username']
            if name in accounts: return httpx.Response(400)
            accounts[name] = (2000 + len(accounts), credentials['password'])
            return httpx.Response(200, json={'access_token': name})
        if path.endswith('/login'):
            credentials = kwargs['json']
            if credentials['username'] in accounts and credentials['password'] == accounts[credentials['username']][1]:
                return httpx.Response(200, json={'access_token': credentials['username']})
            return httpx.Response(401)
        if token in accounts:
            return httpx.Response(200, json={'id': accounts[token][0], 'username': token})
        return httpx.Response(401)
    monkeypatch.setattr(auth, 'hub_request', request)
    # The login router imports the callable directly.
    import app.api.auth as auth_api
    monkeypatch.setattr(auth_api, 'hub_request', request)


@pytest.fixture
def client():
    from fixtures import seed_recipes
    database.init_database()
    seed_recipes()
    with TestClient(app, headers={'Origin': config.SITE_ORIGIN}) as client:
        yield client


def login(client, username='alice'):
    assert client.post('/api/auth/login', json={'username': username, 'password': 'correct'}).status_code == 200


@pytest.fixture
def payload():
    return {'title': 'Testkuchen', 'instructions': 'Backen.', 'ingredients': [
        {'amount': 250, 'unit': 'g', 'ingredient': 'Mehl'}], 'tags': ['Test', 'Süß'],
        'parts': [{'title': 'Glasur', 'instructions': 'Verrühren.', 'ingredients': [
            {'ingredient': 'Schokolade', 'amount': None, 'unit': None}]}]}
