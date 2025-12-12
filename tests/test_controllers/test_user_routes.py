import pytest


def test_get_users_empty(test_client):
    response = test_client.get("/users")
    assert response.status_code == 200
    payload = response.json()
    assert payload == []


def test_create_and_retrieve_user(test_client):
    create_response = test_client.post(
        "/users",
        json={"username": "api_user_1", "email": "api_user1@example.com"},
    )
    assert create_response.status_code in (200, 201)
    created_user = create_response.json()
    user_id = created_user["id"]
    assert created_user["username"] == "api_user_1"

    get_response = test_client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["email"] == "api_user1@example.com"


def test_update_and_delete_user(test_client):
    create_response = test_client.post(
        "/users",
        json={"username": "api_user_2", "email": "api_user2@example.com"},
    )
    user_id = create_response.json()["id"]

    update_response = test_client.put(
        f"/users/{user_id}",
        json={"description": "updated via api"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["description"] == "updated via api"

    delete_response = test_client.delete(f"/users/{user_id}")
    assert delete_response.status_code in (200, 204)

    not_found_response = test_client.get(f"/users/{user_id}")
    assert not_found_response.status_code == 404


def test_get_users_with_filters(test_client):
    # Создаем пользователя для фильтрации
    test_client.post(
        "/users",
        json={"username": "filter_user", "email": "filter@example.com"},
    )

    # Фильтруем по username
    response = test_client.get("/users?username=filter_user")
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 1
    assert users[0]["username"] == "filter_user"


def test_create_user_validation(test_client):
    # Пытаемся создать пользователя без обязательных полей
    response = test_client.post(
        "/users",
        json={},  # Пустой JSON
    )
    # Должна быть ошибка валидации
    assert response.status_code == 400
