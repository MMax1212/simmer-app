"""US3.2.4: lifecycle acceptance against migrated SQLite with real FK enforcement.

Unlike the shared in-memory fixtures, every request gets a fresh Session. This
catches accidental reliance on cached ORM objects instead of committed records.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.main import app
from app.models import Post, PostComment, PostLike, Recipe, SavedPost, User
from tests.conftest import auth_headers
from tests.test_migrations import migrate

BODY = {'caption': 'Original dinner', 'image_url': '/images/dinner.jpg', 'media_type': 'video'}


@pytest.fixture()
def lifecycle(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'lifecycle.db'}", connect_args={'check_same_thread': False})
    migrate(engine)
    engine.dispose()

    @event.listens_for(engine, 'connect')
    def foreign_keys(connection, _):
        connection.execute('PRAGMA foreign_keys=ON')

    def request_session():
        # Match production request boundaries: no identity map survives to the next request.
        with Session(engine) as session:
            yield session

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = request_session
    try:
        with TestClient(app) as client:
            owner = auth_headers(client)
            other = auth_headers(client, email='other@example.com', username='other')
            created = client.post('/api/v1/posts', headers=owner, json=BODY)
            assert created.status_code == 201
            yield client, engine, owner, other, created.json()
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
        engine.dispose()


def test_edit_persists_across_requests_then_delete_is_final(lifecycle):
    client, engine, owner, _, post = lifecycle
    with Session(engine) as session:
        recipe = Recipe(author_id=post['author_id'], title='Keep linked recipe')
        session.add(recipe)
        session.commit()
        recipe_id = recipe.id
    path = f"/api/v1/posts/{post['id']}"
    changed = {**BODY, 'caption': 'Updated dinner', 'recipe_id': recipe_id}
    res = client.put(path, headers=owner, json=changed)
    assert res.status_code == 200
    assert client.get(path).json() == res.json()
    with Session(engine) as session:
        stored = session.get(Post, post['id'])
        assert stored.caption == changed['caption'] and stored.recipe_id == recipe_id
    assert client.delete(path, headers=owner).status_code == 204
    assert client.get(path).status_code == 404
    assert client.put(path, headers=owner, json=changed).status_code == 404
    assert client.delete(path, headers=owner).status_code == 404
    with Session(engine) as session:
        assert session.get(Recipe, recipe_id) is not None
        assert session.get(User, post['author_id']) is not None


@pytest.mark.parametrize('method', ['put', 'delete'])
@pytest.mark.parametrize('credential', ['other', 'invalid', 'inactive'])
def test_denied_writes_leave_committed_post_intact(lifecycle, method, credential):
    client, engine, owner, other, post = lifecycle
    if credential == 'other':
        headers, expected = other, 403
    elif credential == 'invalid':
        headers, expected = {'Authorization': 'Bearer invalid-token'}, 401
    else:
        # A valid existing token must stop working immediately after account deactivation.
        with Session(engine) as session:
            session.get(User, post['author_id']).is_active = False
            session.commit()
        headers, expected = owner, 401
    kwargs = {'json': {**BODY, 'caption': 'Unauthorized change'}} if method == 'put' else {}
    assert getattr(client, method)(f"/api/v1/posts/{post['id']}", headers=headers, **kwargs).status_code == expected
    assert client.get(f"/api/v1/posts/{post['id']}").json() == post


@pytest.mark.parametrize('changes', [
    {'caption': None}, {'image_url': None}, {'media_type': None},
    {'created_at': '2000-01-01T00:00:00Z'}, {'updated_at': '2000-01-01T00:00:00Z'},
])
def test_invalid_edit_does_not_change_persistent_record(lifecycle, changes):
    client, _, owner, _, post = lifecycle
    path = f"/api/v1/posts/{post['id']}"
    assert client.put(path, headers=owner, json={**BODY, **changes}).status_code == 422
    assert client.get(path).json() == post


def test_delete_cleans_other_users_engagement_without_touching_other_posts(lifecycle):
    client, engine, owner, other, post = lifecycle
    second = client.post('/api/v1/posts', headers=other, json={**BODY, 'caption': 'Unrelated dinner'}).json()
    with Session(engine) as session:
        # Confirm FK enforcement is active, not merely declared in model metadata.
        from sqlalchemy import text
        assert session.scalar(text('PRAGMA foreign_keys')) == 1
        for target in [post['id'], second['id']]:
            for model, fields in [(PostLike, {}), (PostComment, {'content': 'Nice'}), (SavedPost, {})]:
                session.add(model(user_id=second['author_id'], post_id=target, **fields))
        session.commit()
    assert client.delete(f"/api/v1/posts/{post['id']}", headers=owner).status_code == 204
    with Session(engine) as session:
        for model in [PostLike, PostComment, SavedPost]:
            assert session.scalars(select(model).where(model.post_id == post['id'])).all() == []
            assert len(session.scalars(select(model).where(model.post_id == second['id'])).all()) == 1
        assert session.get(User, second['author_id']) is not None
    assert client.get(f"/api/v1/posts/{second['id']}").json() == second


@pytest.mark.parametrize('missing', ['caption', 'image_url'])
def test_put_requires_complete_editable_content(lifecycle, missing):
    client, _, owner, _, post = lifecycle
    body = {key: value for key, value in BODY.items() if key != missing}
    path = f"/api/v1/posts/{post['id']}"
    assert client.put(path, headers=owner, json=body).status_code == 422
    assert client.get(path).json() == post


def test_maximum_lengths_and_full_replacement_defaults(lifecycle):
    client, engine, owner, _, post = lifecycle
    path = f"/api/v1/posts/{post['id']}"
    with Session(engine) as session:
        recipe = Recipe(author_id=post['author_id'], title='Existing attachment')
        session.add(recipe)
        session.flush()
        session.get(Post, post['id']).recipe_id = recipe.id
        session.commit()
    # At-limit strings must remain valid. Omitted optional fields follow the PUT contract.
    body = {'caption': 'x' * 2000, 'image_url': 'x' * 1000}
    res = client.put(path, headers=owner, json=body)
    assert res.status_code == 200
    assert res.json()['caption'] == body['caption']
    assert res.json()['image_url'] == body['image_url']
    assert res.json()['media_type'] == 'image'
    assert res.json()['recipe_id'] is None
    assert res.json()['recipe_title'] is None
    assert client.get(path).json() == res.json()
