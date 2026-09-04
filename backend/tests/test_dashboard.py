from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.action import ClimateAction, UserAction
from app.models.assessment import Assessment
from app.models.user import User


def create_user(client, email: str):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Dashboard User", "email": email, "password": "correct-horse-battery-staple"},
    )
    payload = response.json()
    return payload["user"]["id"], {"Authorization": f"Bearer {payload['access_token']}"}


def add_assessment(session, user_id, *, transport=20, energy=80, food=70, waste=60):
    session.add(Assessment(user_id=user_id, answers={}, transport_score=transport, energy_score=energy, food_score=food, waste_score=waste, overall_score=round((transport + energy + food + waste) / 4), lowest_category="transport"))
    session.commit()


def test_dashboard_requires_authentication(client):
    assert client.get("/api/v1/dashboard").status_code == 401


def test_new_user_dashboard_is_empty_and_safe(client):
    _, headers = create_user(client, "dashboard-new@example.com")
    payload = client.get("/api/v1/dashboard", headers=headers).json()
    assert payload["climate_score"] is None
    assert payload["completed_action_count"] == 0
    assert payload["estimated_co2e_avoided"] == 0
    assert payload["recent_activity"] == []
    assert payload["recommendations"] == []


def test_dashboard_uses_owned_assessment_user_and_frozen_action_values(client, db_connection):
    user_id, headers = create_user(client, "dashboard-populated@example.com")
    other_id, other_headers = create_user(client, "dashboard-other@example.com")
    session = Session(bind=db_connection, join_transaction_mode="create_savepoint")
    add_assessment(session, user_id)
    add_assessment(session, other_id, transport=100, energy=10, food=10, waste=10)
    user = session.get(User, user_id)
    user.xp, user.current_streak, user.longest_streak = 345, 3, 8
    actions = list(session.scalars(select(ClimateAction).order_by(ClimateAction.title).limit(2)))
    session.add_all([
        UserAction(user_id=user_id, action_id=actions[0].id, status="completed", completed_at=datetime.now(timezone.utc), xp_awarded=50, estimated_co2e_kg_awarded=Decimal("1.25")),
        UserAction(user_id=user_id, action_id=actions[1].id, status="completed", completed_at=datetime.now(timezone.utc), xp_awarded=80, estimated_co2e_kg_awarded=Decimal("0")),
        UserAction(user_id=other_id, action_id=actions[0].id, status="completed", completed_at=datetime.now(timezone.utc), xp_awarded=999, estimated_co2e_kg_awarded=Decimal("99")),
    ])
    session.commit()
    payload = client.get("/api/v1/dashboard", headers=headers).json()
    assert payload["xp"] == 345 and payload["current_streak"] == 3 and payload["longest_streak"] == 8
    assert payload["climate_score"] == 58 and payload["category_scores"]["transport"] == 20
    assert payload["completed_action_count"] == 2 and float(payload["estimated_co2e_avoided"]) == 1.25
    assert len(payload["recent_activity"]) == 2
    assert all(item["xp_awarded"] != 999 for item in payload["recent_activity"])
    assert payload["recommendations"] and all(item["category"] == "transport" for item in payload["recommendations"])
    assert client.get("/api/v1/dashboard", headers=other_headers).json()["xp"] == 0
    session.close()
