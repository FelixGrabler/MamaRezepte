from copy import deepcopy

from sqlalchemy import func, select
from app.core import database as db
from app.core.catalogue import CATEGORIES
from conftest import login


def writable(recipe):
    fields = ('title', 'instructions', 'ingredients', 'category', 'servings', 'is_public', 'tags')
    payload = {key: recipe[key] for key in fields}
    payload['parts'] = [{key: part[key] for key in ('id', 'title', 'instructions', 'ingredients')} for part in recipe['parts']]
    return payload


def test_felix_owns_and_can_configure_the_original_public_collection(client):
    assert client.get('/api/recipes/48').json()['owner_username'] == 'felix'
    login(client, 'bob')
    assert client.get('/api/recipes/48').json()['can_edit'] is False
    login(client, 'felix')
    original = client.get('/api/recipes/48').json()
    assert original['can_edit'] is True and original['owner_id'] == 1003
    with db.session() as session:
        imported = session.scalars(select(db.Recipe).where(db.Recipe.id <= 88)).all()
        assert len(imported) == 5 and all(recipe.owner_id == 1003 for recipe in imported)
    payload = writable(original)
    payload.update(category='Frühstück', tags=['Familie', 'Mama-Rezept'], servings=6)
    try:
        updated = client.put('/api/recipes/48', json=payload)
        assert updated.status_code == 200, updated.text
        recipe = updated.json()
        assert recipe['category'] == 'Frühstück' and recipe['servings'] == 6
        assert all(part['category'] == recipe['category'] and part['servings'] == 6 for part in recipe['parts'])
        assert [part['id'] for part in recipe['parts']] == [part['id'] for part in original['parts']]
        client.post('/api/auth/logout')
        public = client.get('/api/recipes/48').json()
        assert public['category'] == 'Frühstück' and 'Familie' in public['tags']
        assert public['can_edit'] is False
    finally:
        login(client, 'felix')
        assert client.put('/api/recipes/48', json=writable(original)).status_code == 200


def test_category_tags_filters_validation_and_portion_metadata(client, payload):
    login(client)
    payload.update(category='Suppe', servings=8, tags=['vegetarisch', 'Vegetarisch', 'SÜSS', 'Familienessen'])
    result = client.post('/api/recipes/', json=payload)
    assert result.status_code == 201, result.text
    recipe = result.json()
    rid = recipe['id']
    assert recipe['tags'] == ['Familienessen', 'süß', 'vegetarisch']
    assert recipe['category'] == 'Suppe' and recipe['servings'] == 8
    assert all(part['servings'] == 8 and part['category'] == 'Suppe' for part in recipe['parts'])
    filtered = client.get('/api/recipes/', params=[('category', 'Suppe'), ('tags', 'VEGETARISCH'), ('tags', 'süß')]).json()
    assert rid in [r['id'] for r in filtered]
    assert rid not in [r['id'] for r in client.get('/api/recipes/', params={'category': 'Frühstück'}).json()]
    assert rid not in [r['id'] for r in client.get('/api/recipes/', params=[('tags', 'vegetarisch'), ('tags', 'Fleisch')]).json()]
    assert all(r['category'] in CATEGORIES for r in client.get('/api/recipes/').json())
    assert 'Familienessen' in [tag['name'] for tag in client.get('/api/tags/').json()]
    for field, value in [('category', 'Hauptspeiße'), ('category', 'Nachspeiße'), ('category', 'Unbekannt'), ('servings', 0), ('servings', -1), ('servings', 1.5), ('servings', 1001), ('servings', True)]:
        invalid = deepcopy(payload)
        invalid[field] = value
        assert client.post('/api/recipes/', json=invalid).status_code == 422
    assert client.get('/api/recipes/', params={'category': 'Unbekannt'}).status_code == 422
    login(client, 'bob')
    assert client.put(f'/api/recipes/{rid}', json=payload).status_code == 403
    login(client)
    client.delete(f'/api/recipes/{rid}')


def test_favourites_are_personal_idempotent_and_respect_privacy(client, payload):
    assert client.get('/api/recipes/?favourites=true').status_code == 401
    assert client.put('/api/recipes/48/favourite').status_code == 401
    login(client)
    recipe = client.post('/api/recipes/', json=payload).json()
    rid = recipe['id']
    login(client, 'bob')
    for _ in range(2):
        assert client.put(f'/api/recipes/{rid}/favourite').json() == {'is_favourite': True}
    assert client.get(f'/api/recipes/{rid}').json()['is_favourite'] is True
    assert rid in [r['id'] for r in client.get('/api/recipes/?favourites=true').json()]
    with db.session() as session:
        assert session.scalar(select(func.count()).select_from(db.Favourite).where(db.Favourite.recipe_id == rid)) == 1
    login(client)
    assert client.get(f'/api/recipes/{rid}').json()['is_favourite'] is False
    assert rid not in [r['id'] for r in client.get('/api/recipes/?favourites=true').json()]
    payload['is_public'] = False
    assert client.put(f'/api/recipes/{rid}', json=payload).status_code == 200
    login(client, 'bob')
    assert rid not in [r['id'] for r in client.get('/api/recipes/?favourites=true').json()]
    assert client.put(f'/api/recipes/{rid}/favourite').status_code == 404
    assert client.get(f'/api/recipes/{rid}').status_code == 404
    login(client)
    assert client.put(f'/api/recipes/{rid}/favourite').status_code == 200
    part_id = client.get(f'/api/recipes/{rid}').json()['parts'][0]['id']
    assert client.put(f"/api/recipes/{part_id}/favourite").status_code == 400
    assert client.delete(f'/api/recipes/{rid}/favourite').json() == {'is_favourite': False}
    assert client.delete(f'/api/recipes/{rid}/favourite').json() == {'is_favourite': False}
    client.delete(f'/api/recipes/{rid}')
    with db.session() as session:
        assert session.scalar(select(func.count()).select_from(db.Favourite).where(db.Favourite.recipe_id == rid)) == 0


def test_reordering_parts_preserves_ids_and_rejects_other_recipes_parts(client, payload):
    login(client)
    payload['parts'].append({'title': 'Teig', 'instructions': 'Kneten.', 'ingredients': []})
    recipe = client.post('/api/recipes/', json=payload).json()
    rid = recipe['id']
    edited = writable(recipe)
    edited['parts'].reverse()
    result = client.put(f'/api/recipes/{rid}', json=edited)
    assert result.status_code == 200, result.text
    assert [part['id'] for part in result.json()['parts']] == [part['id'] for part in reversed(recipe['parts'])]
    foreign = deepcopy(edited)
    foreign['parts'][0]['id'] = 49  # Imported pizza dough belongs to recipe 48.
    assert client.put(f'/api/recipes/{rid}', json=foreign).status_code == 422
    duplicate = deepcopy(edited)
    duplicate['parts'][1]['id'] = duplicate['parts'][0]['id']
    assert client.put(f'/api/recipes/{rid}', json=duplicate).status_code == 422
    assert client.post('/api/recipes/', json=edited).status_code == 422
    client.delete(f'/api/recipes/{rid}')
