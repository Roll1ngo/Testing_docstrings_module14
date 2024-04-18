import pytest

from src.conf import messages


test_contact = {"name": "test_contact_name", "last_name": "test_contact_last_name", "email": "test_email@gmail.com",
                "phone_number": "123456789", "birthday": "2024-04-18"}


def test_get_contacts(client, mock_rate_limiter, get_access_token):
    token = get_access_token
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("rest_api/contacts", headers=headers)

    data = response.json()
    assert response.status_code == 200
    assert len(data) == 0


def test_create_contact(client, mock_rate_limiter, get_access_token):
    token = get_access_token
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("rest_api/contacts", json=test_contact, headers=headers)

    data = response.json()
    assert response.status_code == 201
    assert "id" in data
    assert data["name"] == test_contact["name"]
    assert data["email"] == test_contact["email"]
    assert data["phone_number"] == test_contact["phone_number"]


def test_get_contact_wrong_id(client, mock_rate_limiter, get_access_token):
    token = get_access_token
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("rest_api/contacts/9999", headers=headers)

    data = response.json()
    assert response.status_code == 404, response.text
    assert data["detail"] == messages.CONTACT_NOT_FOUND


def test_get_contact(client, mock_rate_limiter, get_access_token):
    token = get_access_token
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("rest_api/contacts/1", headers=headers)

    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "test_contact_name"


def test_update_contact(client, mock_rate_limiter, get_access_token):
    token = get_access_token
    headers = {"Authorization": f"Bearer {token}"}

    response = client.put("rest_api/contacts/1",
                          json={"name": "updated_contact", "last_name": "test_contact", "email": "test_email@gmail.com",
                                "phone_number": "123456789", "birthday": "2022-01-01"}, headers=headers)

    data = response.json()
    assert response.status_code == 201
    assert data["name"] == "updated_contact"
    assert data["email"] == "test_email@gmail.com"
    client.put("rest_api/contacts/1", json=test_contact, headers=headers)


def test_update_contact_if_contact_is_none(client, mock_rate_limiter, get_access_token):
    token = get_access_token
    headers = {"Authorization": f"Bearer {token}"}

    response = client.put("rest_api/contacts/9999",
                          json={"name": "updated_contact", "last_name": "test_contact", "email": "test_email@gmail.com",
                                "phone_number": "123456789", "birthday": "2022-01-01"}, headers=headers)

    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == messages.CONTACT_NOT_FOUND


@pytest.mark.skip(reason="Delete a single contact")
def test_delete_contact(client, mock_rate_limiter, get_access_token):
    token = get_access_token
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("rest_api/contacts/1", headers=headers)

    data = response.json()
    assert response.status_code == 200
    assert data == "test_contact_name test_contact_last_name has been deleted"


def test_delete_contact_if_contact_is_none(client, mock_rate_limiter, get_access_token):
    token = get_access_token
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("rest_api/contacts/9999", headers=headers)

    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == messages.CONTACT_NOT_FOUND


@pytest.mark.skip(reason="In postgres work,here not, can`t fix it")
def test_get_birthdays(client, mock_rate_limiter, get_access_token):
    token = get_access_token
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("rest_api/contacts/birthdate", headers=headers)

    data = response.json()
    assert response.status_code == 200
    assert len(data) == 0


def test_search_contacts(client, mock_rate_limiter, get_access_token):
    token = get_access_token
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"rest_api/contacts/search/{test_contact['name']}", headers=headers)

    data = response.json()
    print(data)
    assert response.status_code == 200
    assert test_contact["email"] in data[0]["email"]
    assert "id" in data[0]
