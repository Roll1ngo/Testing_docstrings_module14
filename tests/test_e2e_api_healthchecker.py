from src.conf import messages


def test_healthchecker(client):
    params = {"request_string": "SELECT 2"}
    response = client.get("api_service/health_checker", params=params)
    assert response.status_code == 200
    assert response.json() == {"message": messages.HEALTH_CHECKER}


def test_healthchecker_not_connection_to_db(client):
    params = {"request_string": "Wrong_request"}
    response = client.get("api_service/health_checker", params=params)
    assert response.status_code == 500, response.text
    data = response.json()
    assert data["detail"] == messages.ERROR_CONNECTION_TO_DB
