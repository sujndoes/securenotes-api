def auth_headers(client, email, password="longenough123"):
    client.post("/register",
				json={"email": email, "password": password})
    response = client.post("/login",
							data={"username": email, "password": password})
    data = response.json()
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_note(client, headers, title="my title", body="my body"):
    return client.post("/notes",
						json={"title": title, "body": body}, headers=headers)


def test_create_note_requires_token(client):
    response = client.post("/notes",
							json={"title": "x", "body": "y"})
    assert response.status_code == 401


def test_create_note(client):
    headers = auth_headers(client, "alice@example.com")
    response = create_note(client, headers, title="hello", body="world")
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "hello"
    assert data["body"] == "world"
    assert "id" in data
    assert "owner_id" not in data


def test_list_only_own_notes(client):
    alice = auth_headers(client, "alice@example.com")
    bob = auth_headers(client, "bob@example.com")
    create_note(client, alice, title="alice 1")
    create_note(client, alice, title="alice 2")
    create_note(client, bob, title="bob 1")

    alice_notes = client.get("/notes", headers=alice).json()
    bob_notes = client.get("/notes", headers=bob).json()

    assert [n["title"] for n in alice_notes] == ["alice 1", "alice 2"]
    assert [n["title"] for n in bob_notes] == ["bob 1"]


def test_get_own_note(client):
    alice = auth_headers(client, "alice@example.com")
    note_id = create_note(client, alice, title="mine").json()["id"]
    response = client.get(f"/notes/{note_id}", headers=alice)
    assert response.status_code == 200
    assert response.json()["title"] == "mine"


def test_cannot_read_other_users_note(client):
    alice = auth_headers(client, "alice@example.com")
    bob = auth_headers(client, "bob@example.com")
    note_id = create_note(client, alice, title="private").json()["id"]

    response = client.get(f"/notes/{note_id}", headers=bob)
    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"

    assert client.get(f"/notes/{note_id}", headers=alice).status_code == 200


def test_cannot_edit_other_users_note(client):
    alice = auth_headers(client, "alice@example.com")
    bob = auth_headers(client, "bob@example.com")
    note_id = create_note(client, alice, title="original").json()["id"]

    response = client.put(
        f"/notes/{note_id}", json={"title": "hacked", "body": "hacked"}, headers=bob
    )
    assert response.status_code == 404

    still_there = client.get(f"/notes/{note_id}", headers=alice).json()
    assert still_there["title"] == "original"


def test_cannot_delete_other_users_note(client):
    alice = auth_headers(client, "alice@example.com")
    bob = auth_headers(client, "bob@example.com")
    note_id = create_note(client, alice).json()["id"]

    response = client.delete(f"/notes/{note_id}", headers=bob)
    assert response.status_code == 404

    assert client.get(f"/notes/{note_id}", headers=alice).status_code == 200


def test_update_own_note(client):
    alice = auth_headers(client, "alice@example.com")
    note_id = create_note(client, alice, title="old").json()["id"]

    response = client.put(
        f"/notes/{note_id}", json={"title": "new", "body": "new body"}, headers=alice
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == "new"


def test_delete_own_note(client):
    alice = auth_headers(client, "alice@example.com")
    note_id = create_note(client, alice).json()["id"]

    response = client.delete(f"/notes/{note_id}", headers=alice)
    assert response.status_code == 204

    assert client.get(f"/notes/{note_id}", headers=alice).status_code == 404
