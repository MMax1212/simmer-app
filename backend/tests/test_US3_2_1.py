"""US3.2.1: API behavior, author-only authorization, and safe deletion."""
import pytest
from sqlalchemy import select
from app.models import Post, PostComment, PostLike, Recipe, SavedPost
from tests.conftest import auth_headers

BODY = {'caption': 'Dinner', 'image_url': 'https://example.com/dinner.jpg', 'media_type': 'image'}

@pytest.fixture()
def own_post(client):
    headers = auth_headers(client)
    res = client.post('/api/v1/posts', headers=headers, json=BODY)
    assert res.status_code == 201
    return headers, res.json()

@pytest.mark.parametrize('method', ['put', 'delete'])
def test_auth_required(client, own_post, method):
    _, post = own_post
    res = getattr(client, method)(f"/api/v1/posts/{post['id']}", **({'json': BODY} if method == 'put' else {}))
    assert res.status_code == 401
    assert client.get(f"/api/v1/posts/{post['id']}").json() == post

@pytest.mark.parametrize('method', ['put', 'delete'])
@pytest.mark.parametrize('admin', [False, True])
def test_only_author_can_modify(client, own_post, make_admin, method, admin):
    _, post = own_post
    other = auth_headers(client, email='other@example.com', username='other')
    if admin:
        make_admin('other@example.com')
    res = getattr(client, method)(f"/api/v1/posts/{post['id']}", headers=other,
                                  **({'json': {**BODY, 'caption': 'Hijacked'}} if method == 'put' else {}))
    assert res.status_code == 403
    assert client.get(f"/api/v1/posts/{post['id']}").json() == post

@pytest.mark.parametrize('method', ['put', 'delete'])
def test_missing_post(client, own_post, method):
    headers, _ = own_post
    res = getattr(client, method)('/api/v1/posts/999999', headers=headers,
                                  **({'json': BODY} if method == 'put' else {}))
    assert res.status_code == 404

@pytest.mark.parametrize('changes', [
    {'caption': ''}, {'caption': '   '}, {'caption': 'x'*2001},
    {'image_url': ''}, {'image_url': '  '}, {'image_url': 'x'*1001},
    {'media_type': 'audio'}, {'author_id': 999}, {'id': 999},
])
def test_invalid_update_is_atomic(client, own_post, changes):
    headers, post = own_post
    res = client.put(f"/api/v1/posts/{post['id']}", headers=headers, json={**BODY, **changes})
    assert res.status_code == 422
    assert client.get(f"/api/v1/posts/{post['id']}").json() == post


def test_update_and_detach_recipe(client, own_post, db_session):
    headers, post = own_post
    recipe = Recipe(author_id=post['author_id'], title='Linked recipe')
    db_session.add(recipe)
    db_session.commit()
    body = {**BODY, 'caption': 'New caption', 'image_url': 'https://example.com/new.mp4',
            'media_type': 'video', 'recipe_id': recipe.id}
    res = client.put(f"/api/v1/posts/{post['id']}", headers=headers, json=body)
    assert res.status_code == 200
    updated = res.json()
    assert {k: updated[k] for k in body} == body
    assert updated['author_id'] == post['author_id']
    assert updated['created_at'] == post['created_at']
    assert updated['updated_at'] > post['updated_at']
    assert updated['recipe_title'] == recipe.title
    assert client.get(f"/api/v1/posts/{post['id']}").json() == updated
    # PUT replaces the editable representation; null removes the optional recipe link.
    res = client.put(f"/api/v1/posts/{post['id']}", headers=headers, json={**body, 'recipe_id': None})
    assert res.json()['recipe_title'] is None
    assert res.json()['recipe_id'] is None


def test_missing_recipe_does_not_partially_update(client, own_post):
    headers, post = own_post
    res = client.put(f"/api/v1/posts/{post['id']}", headers=headers,
                     json={**BODY, 'caption': 'Must not persist', 'recipe_id': 999999})
    assert res.status_code == 404
    assert client.get(f"/api/v1/posts/{post['id']}").json() == post


def test_delete_cleans_dependents_but_preserves_recipe(client, own_post, db_session):
    headers, post = own_post
    recipe = Recipe(author_id=post['author_id'], title='Keep recipe')
    db_session.add(recipe)
    db_session.flush()
    entity = db_session.get(Post, post['id'])
    entity.recipe_id = recipe.id
    # Populate all child relationships to verify actual cleanup, not just an empty delete.
    for model, extra in [(PostLike, {}), (PostComment, {'content': 'Good'}), (SavedPost, {})]:
        db_session.add(model(post_id=entity.id, user_id=entity.author_id, **extra))
    db_session.commit()
    res = client.delete(f"/api/v1/posts/{post['id']}", headers=headers)
    assert res.status_code == 204 and res.content == b''
    assert client.get(f"/api/v1/posts/{post['id']}").status_code == 404
    for model in (PostLike, PostComment, SavedPost):
        assert db_session.scalars(select(model).where(model.post_id == post['id'])).all() == []
    assert db_session.get(Recipe, recipe.id) is not None
