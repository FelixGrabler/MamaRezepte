"""Real backup/recovery check, enabled only for a dedicated Postgres test DB."""
import io
import os
from pathlib import Path
import subprocess

import pytest
from sqlalchemy import text
from PIL import Image
from conftest import login

from app.core import database as db, config


def test_postgres_backup_restore_and_retention(client, tmp_path, payload):
    if db.engine.dialect.name != 'postgresql':
        pytest.skip('Run with a dedicated PostgreSQL test database and pg_dump/pg_restore on PATH')
    import shutil
    if not shutil.which('pg_dump') or not shutil.which('pg_restore'):
        pytest.skip('PostgreSQL client tools are required for recovery test')
    root = Path(__file__).resolve().parents[2]
    url = db.engine.url
    images = config.UPLOAD_DIR
    login(client)
    payload.update(is_public=False, category='Nachspeiße', servings=6, tags=['süß', 'Familienessen'])
    recipe = client.post('/api/recipes/', json=payload).json()
    rid = recipe['id']
    raw = io.BytesIO()
    Image.new('RGB', (50, 50), 'green').save(raw, 'PNG')
    uploaded = client.post(f'/api/recipes/{rid}/image', files={'image': ('photo.png', raw.getvalue(), 'image/png')}).json()
    photo = images / uploaded['image_path'].removeprefix('uploads/')
    original_image = photo.read_bytes()
    assert client.put(f'/api/recipes/{rid}/favourite').status_code == 200
    original_recipe = client.get(f'/api/recipes/{rid}').json()
    password = tmp_path / 'password'
    password.write_text(url.password or '')
    backups = tmp_path / 'backups'
    backups.mkdir()
    # Retention must only remove old completed snapshots.
    for day in range(1, 10):
        (backups / f'202001{day:02d}T120000Z').mkdir()
    unrelated = backups / 'keep-this'
    unrelated.mkdir()
    env = dict(os.environ, PGHOST=url.host or 'localhost', PGPORT=str(url.port or 5432),
               PGUSER=url.username, PGDATABASE=url.database, PASSWORD_FILE=str(password),
               UPLOAD_ROOT=str(images), BACKUP_ROOT=str(backups), BACKUP_KEEP='8')
    before = client.get('/api/recipes/48').json()
    subprocess.run(['sh', str(root / 'ops/backup.sh')], env=env, check=True)
    completed = sorted(p.name for p in backups.iterdir() if p.is_dir() and p.name.endswith('Z'))
    assert len(completed) == 8 and unrelated.exists()
    stamp = completed[-1]
    assert (backups / 'last-success').exists()
    # Lose the schema and uploads, simulating accidental data deletion.
    with db.engine.begin() as conn:
        for table in reversed(db.Base.metadata.sorted_tables):
            conn.execute(text(f'DROP TABLE {table.name} CASCADE'))
    photo.unlink()
    subprocess.run(['sh', str(root / 'ops/restore.sh'), stamp], env=env, check=True)
    assert client.get('/api/recipes/48').json() == before
    assert photo.read_bytes() == original_image
    assert client.get(f'/api/recipes/{rid}').json() == original_recipe
    assert client.get(f'/api/recipes/{rid}/image').content == original_image
    assert subprocess.run(['flock', '-n', str(backups / '.lock'), 'true']).returncode == 0
    # A corrupt archive must fail before changing the restored database.
    with (backups / stamp / 'database.dump').open('ab') as file:
        file.write(b'corruption')
    result = subprocess.run(['sh', str(root / 'ops/restore.sh'), stamp], env=env)
    assert result.returncode != 0
    assert client.get('/api/recipes/48').json() == before
    assert subprocess.run(['flock', '-n', str(backups / '.lock'), 'true']).returncode == 0

    client.delete(f'/api/recipes/{rid}')
