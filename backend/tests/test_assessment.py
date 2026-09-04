from app.services.assessment_service import QUESTIONS


def register_and_token(client, email="assessment@example.com"):
    response = client.post("/api/v1/auth/register", json={"name": "Assessment User", "email": email, "password": "correct-horse-battery-staple"})
    return response.json()["access_token"], response.json()["user"]["id"]


def valid_answers():
    return {question.id: question.options[0].id for question in QUESTIONS}


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_questions_are_public_and_do_not_expose_scores(client):
    response = client.get("/api/v1/assessment/questions")
    assert response.status_code == 200
    assert len(response.json()) == 12
    assert "score" not in response.json()[0]["options"][0]


def test_assessment_requires_authentication(client):
    assert client.post("/api/v1/assessment", json={"answers": valid_answers()}).status_code == 401


def test_assessment_persists_and_scores_correctly(client):
    token, user_id = register_and_token(client)
    response = client.post("/api/v1/assessment", json={"answers": valid_answers()}, headers=auth_headers(token))
    assert response.status_code == 201
    result = response.json()
    assert result["overall_score"] == 100
    assert result["lowest_category"] == "transport"
    assert all(0 <= result[key] <= 100 for key in ("transport_score", "energy_score", "food_score", "waste_score", "overall_score"))
    latest = client.get("/api/v1/assessment/latest", headers=auth_headers(token))
    assert latest.status_code == 200
    assert latest.json()["id"] == result["id"]
    assert user_id


def test_invalid_question_option_and_missing_answers_are_rejected(client):
    token, _ = register_and_token(client)
    headers = auth_headers(token)
    unknown = valid_answers() | {"UNKNOWN": "anything"}
    assert client.post("/api/v1/assessment", json={"answers": unknown}, headers=headers).status_code == 422
    invalid_option = valid_answers() | {"T1": "invalid"}
    assert client.post("/api/v1/assessment", json={"answers": invalid_option}, headers=headers).status_code == 422
    missing = valid_answers()
    missing.pop("T1")
    assert client.post("/api/v1/assessment", json={"answers": missing}, headers=headers).status_code == 422


def test_latest_is_user_scoped_and_newest(client):
    token_one, _ = register_and_token(client, "one@example.com")
    token_two, _ = register_and_token(client, "two@example.com")
    first = client.post("/api/v1/assessment", json={"answers": valid_answers()}, headers=auth_headers(token_one)).json()
    changed = valid_answers() | {"T1": "private_car"}
    newest = client.post("/api/v1/assessment", json={"answers": changed}, headers=auth_headers(token_one)).json()
    assert client.get("/api/v1/assessment/latest", headers=auth_headers(token_one)).json()["id"] == newest["id"]
    assert client.get("/api/v1/assessment/latest", headers=auth_headers(token_two)).status_code == 404
    assert first["id"] != newest["id"]
