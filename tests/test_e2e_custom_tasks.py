from tests.test_e2e_users import test_user


def test_get_signup_users(client):
    response = client.get("custom_tasks/get_users")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["email"] == test_user["email"]
    assert data[0]["username"] == test_user["username"]
