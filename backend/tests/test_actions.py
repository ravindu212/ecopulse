from app.services.assessment_service import QUESTIONS

def test_action_list_filters(client):
 all_actions=client.get("/api/v1/actions").json(); assert len(all_actions)==16
 sample=all_actions[0]
 filtered=client.get("/api/v1/actions",params={"category":sample["category"],"difficulty":sample["difficulty"],"impact_level":sample["impact_level"]})
 assert filtered.status_code==200 and filtered.json()
 assert all(action["category"]==sample["category"] and action["difficulty"]==sample["difficulty"] and action["impact_level"]==sample["impact_level"] for action in filtered.json())

def test_action_completion_awards_xp_once_and_is_user_scoped(client):
 r=client.post("/api/v1/auth/register",json={"name":"Action User","email":"actions@example.com","password":"correct-horse-battery-staple"}); token=r.json()["access_token"]; headers={"Authorization":f"Bearer {token}"}
 answers={q.id:q.options[-1].id for q in QUESTIONS}; assert client.post("/api/v1/assessment",json={"answers":answers},headers=headers).status_code==201
 recommended=client.get("/api/v1/actions/recommended",headers=headers); assert recommended.status_code==200 and recommended.json()[0]["recommendation_reason"]
 action=recommended.json()[0]; first=client.post(f"/api/v1/actions/{action['id']}/complete",headers=headers); assert first.status_code==200; payload=first.json(); assert payload["xp_awarded"]==action["xp_reward"] and payload["current_streak"]==1
 second=client.post(f"/api/v1/actions/{action['id']}/complete",headers=headers); assert second.status_code==200 and second.json()["xp"]==payload["xp"]
 history=client.get("/api/v1/actions/me",headers=headers); assert len(history.json())==1
 assert client.get("/api/v1/actions/recommended").status_code==401
