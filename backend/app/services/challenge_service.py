from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.models.challenge import Challenge, ChallengeAction
from app.models.challenge import UserChallenge
from app.models.action import UserAction
from app.schemas.challenge import ChallengeActionItem,ChallengeOut
def serialize(c): return ChallengeOut(id=c.id,title=c.title,slug=c.slug,description=c.description,active=c.active,required_actions=[ChallengeActionItem(id=x.action.id,title=x.action.title,slug=x.action.slug,category=x.action.category,difficulty=x.action.difficulty,sort_order=x.sort_order) for x in sorted(c.challenge_actions,key=lambda x:x.sort_order)])
def active(db): return [serialize(c) for c in db.scalars(select(Challenge).options(joinedload(Challenge.challenge_actions).joinedload(ChallengeAction.action)).where(Challenge.active.is_(True)).order_by(Challenge.title)).unique()]
def one(db,id):
 c=db.scalar(select(Challenge).options(joinedload(Challenge.challenge_actions).joinedload(ChallengeAction.action)).where(Challenge.id==id,Challenge.active.is_(True)))
 return serialize(c) if c else None
def join(db,user_id,challenge_id):
 challenge=db.scalar(select(Challenge).where(Challenge.id==challenge_id,Challenge.active.is_(True)))
 if not challenge:return None,None
 membership=db.scalar(select(UserChallenge).where(UserChallenge.user_id==user_id,UserChallenge.challenge_id==challenge.id))
 if not membership: membership=UserChallenge(user_id=user_id,challenge_id=challenge.id,status="active");db.add(membership);db.commit();db.refresh(membership)
 return challenge,membership
def calculate_progress(db,membership):
 ids=list(db.scalars(select(ChallengeAction.action_id).where(ChallengeAction.challenge_id==membership.challenge_id)))
 if not ids:return {"completed_required_actions":0,"total_required_actions":0,"progress_percent":0.0}
 completed=set(db.scalars(select(UserAction.action_id).where(UserAction.user_id==membership.user_id,UserAction.status=="completed",UserAction.action_id.in_(ids))))
 total=len(set(ids));count=len(completed)
 return {"completed_required_actions":count,"total_required_actions":total,"progress_percent":round(count/total*100,2)}

def sync_completion(db,membership,progress):
 if membership.status=="completed": return False
 if progress["total_required_actions"]>0 and progress["completed_required_actions"]==progress["total_required_actions"]:
  membership.status="completed"
  membership.completed_at=datetime.now(timezone.utc)
  return True
 return False

def memberships(db,user_id):
 rows=list(db.scalars(select(UserChallenge).options(joinedload(UserChallenge.challenge).joinedload(Challenge.challenge_actions)).where(UserChallenge.user_id==user_id).order_by(UserChallenge.joined_at.desc())).unique())
 result=[]; changed=False
 for m in rows:
  c=m.challenge;p=calculate_progress(db,m);changed=sync_completion(db,m,p) or changed;result.append((c,m,p["completed_required_actions"],p["total_required_actions"],p["progress_percent"]))
 if changed: db.commit()
 return result
