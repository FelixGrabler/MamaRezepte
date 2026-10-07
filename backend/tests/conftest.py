import os
import sys
import tempfile
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
workspace = Path(tempfile.mkdtemp(prefix="mamarezepte-tests-"))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{workspace}/test.db")
os.environ["LEGACY_DATABASE"] = str(BACKEND / 'data/recipes.db')
os.environ["LEGACY_IMAGES"] = str(BACKEND.parent / 'frontend/public/data/images')
os.environ["UPLOAD_DIR"] = str(workspace / 'uploads')
os.environ["COOKIE_SECURE"] = "false"
os.environ["SITE_ORIGIN"] = "http://testserver"

from fastapi.testclient import TestClient
from app.main import app
from app.core import auth, database, config


@pytest.fixture(autouse=True)
def mock_hub(monkeypatch):
    import httpx
    def request(method, path, **kwargs):
        token = kwargs.get('headers', {}).get('Authorization', '').removeprefix('Bearer ')
        if path.endswith('/login'):
            credentials = kwargs['json']
            if credentials['password'] == 'correct' and credentials['username'] in {'alice', 'bob', 'felix'}:
                return httpx.Response(200, json={'access_token': credentials['username']})
            return httpx.Response(401)
        if token in {'alice', 'bob', 'felix'}:
            return httpx.Response(200, json={'id': {'alice': 1001, 'bob': 1002, 'felix': 1003}[token], 'username': token})
        return httpx.Response(401)
    monkeypatch.setattr(auth, 'hub_request', request)
    # The login router imports the callable directly.
    import app.api.auth as auth_api
    monkeypatch.setattr(auth_api, 'hub_request', request)


@pytest.fixture
def client():
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
