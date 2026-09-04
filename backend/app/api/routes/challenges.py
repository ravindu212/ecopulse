from fastapi import APIRouter, HTTPException
from app.api.deps import CurrentUser, DbSession
from app.schemas.challenge import ChallengeOut, JoinedChallengeOut
from app.services.challenge_service import active, join, memberships, one

router = APIRouter(prefix="/challenges", tags=["challenges"])

@router.get("", response_model=list[ChallengeOut])
def listing(db: DbSession): return active(db)

@router.get("/me", response_model=list[JoinedChallengeOut])
def mine(current_user: CurrentUser, db: DbSession):
 return [JoinedChallengeOut(challenge_id=c.id,title=c.title,slug=c.slug,status=m.status,joined_at=m.joined_at,completed_at=m.completed_at,completed_required_actions=count,total_required_actions=total,progress_percent=pct) for c,m,count,total,pct in memberships(db,current_user.id)]

@router.post("/{challenge_id}/join", response_model=JoinedChallengeOut)
def join_challenge(challenge_id: str, current_user: CurrentUser, db: DbSession):
 challenge,membership=join(db,current_user.id,challenge_id)
 if not challenge: raise HTTPException(404,"Challenge not found")
 return JoinedChallengeOut(challenge_id=challenge.id,title=challenge.title,slug=challenge.slug,status=membership.status,joined_at=membership.joined_at,completed_at=membership.completed_at,completed_required_actions=0,total_required_actions=len(challenge.challenge_actions),progress_percent=0.0)

@router.get("/{challenge_id}", response_model=ChallengeOut)
def detail(challenge_id: str, db: DbSession):
 result=one(db,challenge_id)
 if not result: raise HTTPException(404,"Challenge not found")
 return result
