from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.action import ClimateAction, UserAction
from app.models.assessment import Assessment
from app.models.user import User


def register(client, email):
    response = client.post("/api/v1/auth/register", json={"name": "Progress User", "email": email, "password": "correct-horse-battery-staple"})
    return response.json()["user"]["id"], {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_progress_requires_authentication_and_returns_safe_empty_state(client):
    assert client.get("/api/v1/progress").status_code == 401
    _, headers = register(client, "progress-empty@example.com")
    response = client.get("/api/v1/progress", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"] == {"xp": 0, "current_streak": 0, "longest_streak": 0, "completed_actions": 0, "estimated_co2e_kg_avoided": 0.0}
    assert payload["assessment_history"] == [] and payload["recent_activity"] == []
    assert payload["category_activity"] == [
        {"category": category, "completed_actions": 0, "estimated_co2e_kg_avoided": 0.0}
        for category in ("transport", "energy", "food", "waste")
    ]


def test_progress_uses_frozen_user_data_and_keeps_other_users_out(client, db_connection):
    user_id, headers = register(client, "progress-data@example.com")
    other_id, other_headers = register(client, "progress-other@example.com")
    session = Session(bind=db_connection, join_transaction_mode="create_savepoint")
    actions = {action.category: action for action in session.query(ClimateAction).all()}
    now = datetime.now(timezone.utc)
    user = session.get(User, user_id)
    user.xp, user.current_streak, user.longest_streak = 245, 3, 7
    session.add_all([
        UserAction(user_id=user_id, action_id=actions["transport"].id, status="completed", completed_at=now - timedelta(days=2), xp_awarded=50, estimated_co2e_kg_awarded=Decimal("1.50")),
        UserAction(user_id=user_id, action_id=actions["energy"].id, status="completed", completed_at=now - timedelta(days=1), xp_awarded=80, estimated_co2e_kg_awarded=Decimal("2.25")),
        UserAction(user_id=user_id, action_id=actions["food"].id, status="started", xp_awarded=0, estimated_co2e_kg_awarded=Decimal("0")),
        UserAction(user_id=user_id, action_id=actions["waste"].id, status="cancelled", xp_awarded=0, estimated_co2e_kg_awarded=Decimal("0")),
        UserAction(user_id=other_id, action_id=actions["transport"].id, status="completed", completed_at=now, xp_awarded=999, estimated_co2e_kg_awarded=Decimal("99.99")),
        Assessment(user_id=user_id, answers={}, transport_score=40, energy_score=50, food_score=60, waste_score=70, overall_score=55, lowest_category="transport", created_at=now - timedelta(days=3)),
        Assessment(user_id=user_id, answers={}, transport_score=70, energy_score=80, food_score=90, waste_score=60, overall_score=75, lowest_category="waste", created_at=now - timedelta(days=1)),
        Assessment(user_id=other_id, answers={}, transport_score=1, energy_score=1, food_score=1, waste_score=1, overall_score=1, lowest_category="transport", created_at=now),
    ])
    session.commit()

    response = client.get("/api/v1/progress", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"] == {"xp": 245, "current_streak": 3, "longest_streak": 7, "completed_actions": 2, "estimated_co2e_kg_avoided": 3.75}
    categories = {item["category"]: item for item in payload["category_activity"]}
    assert categories["transport"] == {"category": "transport", "completed_actions": 1, "estimated_co2e_kg_avoided": 1.5}
    assert categories["energy"] == {"category": "energy", "completed_actions": 1, "estimated_co2e_kg_avoided": 2.25}
    assert categories["food"]["completed_actions"] == 0 and categories["waste"]["estimated_co2e_kg_avoided"] == 0.0
    assert [item["overall_score"] for item in payload["assessment_history"]] == [55, 75]
    assert all(isinstance(item["overall_score"], int) for item in payload["assessment_history"])
    assert [item["title"] for item in payload["recent_activity"]] == [actions["energy"].title, actions["transport"].title]
    assert payload["recent_activity"][0]["estimated_co2e_kg_awarded"] == 2.25
    assert client.get("/api/v1/progress", headers=other_headers).json()["summary"]["completed_actions"] == 1
