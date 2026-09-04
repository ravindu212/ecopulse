from datetime import datetime, timezone
from uuid import UUID

from app.schemas.challenge import JoinedChallengeOut


def test_joined_challenge_progress_serializes_as_numbers():
    payload = JoinedChallengeOut(
        challenge_id=UUID("00000000-0000-0000-0000-000000000001"),
        title="Low-Carbon Commute",
        slug="low-carbon-commute",
        status="active",
        joined_at=datetime.now(timezone.utc),
        completed_at=None,
        completed_required_actions=1,
        total_required_actions=3,
        progress_percent=33.33,
    ).model_dump(mode="json")

    assert payload["completed_required_actions"] == 1
    assert payload["total_required_actions"] == 3
    assert payload["progress_percent"] == 33.33
    assert isinstance(payload["progress_percent"], float)
