def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Wilkommen bei der PAPI BOT API"}

def test_create_user(client, test_db):
    user_data = {
        "email": "test@test.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "Hallo123",
        "confirm_password": "Hallo123"
    }
    response = client.post("/users", json=user_data)
    print(response.json())
    assert response.status_code == 200
    assert response.json()["email"] == "test@test.com"
    assert response.json()["first_name"] == "Test"
    assert response.json()["last_name"] == "User"
    # Password should not be returned in response
    assert "password" not in response.json()

def test_delete_user(client, test_user, auth_headers):
    user_id = test_user.id
    response = client.delete(f"/users/{user_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == "User deleted successfully"