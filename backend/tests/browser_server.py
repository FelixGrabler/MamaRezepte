"""Isolated API fixture for browser tests; never used by the application image."""
import os
import tempfile
from pathlib import Path
import sys

backend = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend))
workspace = Path(tempfile.mkdtemp(prefix='mamarezepte-browser-'))
os.environ.update(DATABASE_URL=f'sqlite:///{workspace}/recipes.db',
                  IMAGE_DIR=str(backend / 'images'),
                  UPLOAD_DIR=str(workspace / 'uploads'), COOKIE_SECURE='false',
                  SITE_ORIGIN='http://localhost:15173')
import httpx
import uvicorn
from app.core import auth
from app.api import auth as auth_api
from app.main import app


accounts = {name: (id, 'test-password') for name, id in {'alice': 1001, 'bob': 1002, 'felix': 1003}.items()}

def mock_hub(method, path, **kwargs):
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


auth.hub_request = mock_hub
auth_api.hub_request = mock_hub
from app.core.database import init_database
from fixtures import seed_recipes
init_database()
seed_recipes()
uvicorn.run(app, host='127.0.0.1', port=18051)
