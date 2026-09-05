from sqlalchemy import select,func
from sqlalchemy.orm import Session
from app.models.challenge import Challenge,UserChallenge
def user(client,email):
 r=client.post('/api/v1/auth/register',json={'name':'Challenge User','email':email,'password':'correct-horse-battery-staple'});return r.json()['user']['id'],{'Authorization':f"Bearer {r.json()['access_token']}"}
def test_readonly_and_join(client,db_connection):
 challenges=client.get('/api/v1/challenges');assert challenges.status_code==200 and len(challenges.json())>=3
 item=challenges.json()[0];assert item['required_actions']==sorted(item['required_actions'],key=lambda x:x['sort_order']);assert client.get(f"/api/v1/challenges/{item['id']}").status_code==200;assert client.get('/api/v1/challenges/00000000-0000-0000-0000-000000000000').status_code==404;assert client.post(f"/api/v1/challenges/{item['id']}/join").status_code==401
 uid,h=user(client,'join@example.com');first=client.post(f"/api/v1/challenges/{item['id']}/join",headers=h);assert first.status_code==200 and first.json()['completed_at'] is None and first.json()['status']=='active';second=client.post(f"/api/v1/challenges/{item['id']}/join",headers=h);assert second.json()['joined_at']==first.json()['joined_at'];assert db_connection.execute(select(func.count(UserChallenge.id)).where(UserChallenge.user_id==uid)).scalar_one()==1
 other,_=user(client,'join-other@example.com');assert db_connection.execute(select(func.count(UserChallenge.id)).where(UserChallenge.user_id==other)).scalar_one()==0
 assert client.post('/api/v1/challenges/00000000-0000-0000-0000-000000000000/join',headers=h).status_code==404

def test_my_challenges_are_scoped_and_progress_is_derived(client):
 assert client.get('/api/v1/challenges/me').status_code==401
 _,empty=user(client,'me-empty@example.com');assert client.get('/api/v1/challenges/me',headers=empty).json()==[]
 _,first=user(client,'me-first@example.com');_,second=user(client,'me-second@example.com');challenge=client.get('/api/v1/challenges').json()[0];joined=client.post(f"/api/v1/challenges/{challenge['id']}/join",headers=first).json();client.post(f"/api/v1/challenges/{challenge['id']}/join",headers=second)
 item=client.get('/api/v1/challenges/me',headers=first).json()[0];assert {'challenge_id','title','slug','status','joined_at','completed_at','completed_required_actions','total_required_actions','progress_percent'}<=set(item);assert isinstance(item['progress_percent'],float) and item['progress_percent']==0.0
 action=challenge['required_actions'][0]['id'];client.post(f'/api/v1/actions/{action}/start',headers=first);assert client.get('/api/v1/challenges/me',headers=first).json()[0]['completed_required_actions']==0
 client.post(f'/api/v1/actions/{action}/complete',headers=second);assert client.get('/api/v1/challenges/me',headers=first).json()[0]['completed_required_actions']==0
 client.post(f'/api/v1/actions/{action}/complete',headers=first);item=client.get('/api/v1/challenges/me',headers=first).json()[0];assert item['completed_required_actions']==1 and item['progress_percent']>0 and item['status']=='active' and item['completed_at'] is None
 for required in challenge['required_actions'][1:]:client.post(f"/api/v1/actions/{required['id']}/complete",headers=first)
 item=client.get('/api/v1/challenges/me',headers=first).json()[0];assert item['progress_percent']==100.0 and item['status']=='completed' and item['completed_at'] is not None
 assert client.get('/api/v1/challenges/me',headers=second).json()[0]['completed_required_actions']==1

def test_completion_is_idempotent_and_does_not_award_extra_xp(client,db_connection):
 user_id,headers=user(client,'completion@example.com');challenge=client.get('/api/v1/challenges').json()[0]
 client.post(f"/api/v1/challenges/{challenge['id']}/join",headers=headers)
 for required in challenge['required_actions']:
  client.post(f"/api/v1/actions/{required['id']}/complete",headers=headers)
 xp_after_actions=client.get('/api/v1/auth/me',headers=headers).json()['xp']
 first=client.get('/api/v1/challenges/me',headers=headers).json()[0]
 second=client.get('/api/v1/challenges/me',headers=headers).json()[0]
 assert first['status']=='completed' and first['completed_at'] is not None and first['progress_percent']==100.0
 assert second['status']=='completed' and second['completed_at']==first['completed_at']
 assert client.get('/api/v1/auth/me',headers=headers).json()['xp']==xp_after_actions
 assert db_connection.execute(select(func.count(UserChallenge.id)).where(UserChallenge.challenge_id==challenge['id'],UserChallenge.user_id==user_id)).scalar_one()==1

def test_completion_ignores_started_unrelated_and_other_user_actions(client):
 _,headers=user(client,'completion-scope@example.com');_,other_headers=user(client,'completion-scope-other@example.com')
 challenge=client.get('/api/v1/challenges').json()[0]
 client.post(f"/api/v1/challenges/{challenge['id']}/join",headers=headers)
 linked=challenge['required_actions'][0]['id']
 unrelated=next(action['id'] for action in client.get('/api/v1/actions').json() if action['id'] not in {item['id'] for item in challenge['required_actions']})
 client.post(f'/api/v1/actions/{linked}/start',headers=headers)
 client.post(f'/api/v1/actions/{linked}/complete',headers=other_headers)
 client.post(f'/api/v1/actions/{unrelated}/complete',headers=headers)
 item=client.get('/api/v1/challenges/me',headers=headers).json()[0]
 assert item['status']=='active' and item['completed_at'] is None and item['completed_required_actions']==0

def test_prejoin_completions_sync_without_extra_xp(client):
 _,headers=user(client,'prejoin-completion@example.com');challenge=client.get('/api/v1/challenges').json()[0]
 for required in challenge['required_actions']:
  client.post(f"/api/v1/actions/{required['id']}/complete",headers=headers)
 xp_after_actions=client.get('/api/v1/auth/me',headers=headers).json()['xp']
 client.post(f"/api/v1/challenges/{challenge['id']}/join",headers=headers)
 item=client.get('/api/v1/challenges/me',headers=headers).json()[0]
 assert item['status']=='completed' and item['completed_at'] is not None and item['progress_percent']==100.0
 assert client.get('/api/v1/auth/me',headers=headers).json()['xp']==xp_after_actions

def test_zero_action_challenge_does_not_complete(client,db_connection):
 _,headers=user(client,'zero-challenge@example.com')
 session=Session(bind=db_connection,join_transaction_mode='create_savepoint')
 challenge=Challenge(title='No steps',slug='no-steps',description='No required actions',active=True)
 session.add(challenge);session.flush();challenge_id=challenge.id;session.commit();session.close()
 client.post(f'/api/v1/challenges/{challenge_id}/join',headers=headers)
 item=next(item for item in client.get('/api/v1/challenges/me',headers=headers).json() if item['challenge_id']==str(challenge_id))
 assert item['status']=='active' and item['completed_at'] is None
 assert item['completed_required_actions']==0 and item['total_required_actions']==0 and item['progress_percent']==0.0
