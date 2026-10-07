"""Isolated API fixture for browser tests; never used by the application image."""
import os
import tempfile
from pathlib import Path
import sys

backend = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend))
workspace = Path(tempfile.mkdtemp(prefix='mamarezepte-browser-'))
os.environ.update(DATABASE_URL=f'sqlite:///{workspace}/recipes.db',
                  LEGACY_DATABASE=str(backend / 'data/recipes.db'),
                  LEGACY_IMAGES=str(backend.parent / 'frontend/public/data/images'),
                  UPLOAD_DIR=str(workspace / 'uploads'), COOKIE_SECURE='false',
                  SITE_ORIGIN='http://localhost:15173')
import httpx
import uvicorn
from app.core import auth
from app.api import auth as auth_api
from app.main import app


def mock_hub(method, path, **kwargs):
    token = kwargs.get('headers', {}).get('Authorization', '').removeprefix('Bearer ')
    if path.endswith('/login'):
        credentials = kwargs['json']
        if credentials['username'] in ('alice', 'bob', 'felix') and credentials['password'] == 'test-password':
            return httpx.Response(200, json={'access_token': credentials['username']})
        return httpx.Response(401)
    if token in ('alice', 'bob', 'felix'):
        return httpx.Response(200, json={'id': {'alice': 1001, 'bob': 1002, 'felix': 1003}[token], 'username': token})
    return httpx.Response(401)


auth.hub_request = mock_hub
auth_api.hub_request = mock_hub
uvicorn.run(app, host='127.0.0.1', port=18051)
