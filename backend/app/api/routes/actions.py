from datetime import date, datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.api.deps import CurrentUser, DbSession
from app.models.action import ClimateAction, UserAction
from app.models.assessment import Assessment
from app.schemas.action import ActionOut, CompletionOut, RecommendedAction, UserActionOut

router=APIRouter(prefix="/actions", tags=["actions"])
@router.get("", response_model=list[ActionOut])
def list_actions(db:DbSession, category:str|None=None):
 q=select(ClimateAction).where(ClimateAction.active.is_(True)); q=q.where(ClimateAction.category==category) if category else q
 return list(db.scalars(q.order_by(ClimateAction.title)))
@router.get("/recommended",response_model=list[RecommendedAction])
def recommended(current_user:CurrentUser,db:DbSession):
 assessment=db.scalar(select(Assessment).where(Assessment.user_id==current_user.id).order_by(Assessment.created_at.desc()).limit(1))
 if not assessment: raise HTTPException(404,"Complete an assessment first")
 scores={"transport":assessment.transport_score,"energy":assessment.energy_score,"food":assessment.food_score,"waste":assessment.waste_score}; categories=sorted(scores,key=lambda c:(scores[c],c)); actions=list(db.scalars(select(ClimateAction).where(ClimateAction.active.is_(True)).order_by(ClimateAction.title)))
 result=[]
 for category in categories:
  for action in actions:
   if action.category==category and not any(item.id==action.id for item in result): result.append(action)
   if len(result)>=3: break
  if len(result)>=3: break
 return [RecommendedAction(**ActionOut.model_validate(action).model_dump(), recommendation_reason=f"Recommended because {action.category} was one of your lowest assessment categories.") for action in result]
@router.get("/me",response_model=list[UserActionOut])
def mine(current_user:CurrentUser,db:DbSession): return list(db.scalars(select(UserAction).where(UserAction.user_id==current_user.id).order_by(UserAction.created_at.desc())))
@router.get("/{action_id}",response_model=ActionOut)
def detail(action_id:str,db:DbSession):
 action=db.get(ClimateAction,action_id)
 if not action or not action.active: raise HTTPException(404,"Action not found")
 return action
@router.post("/{action_id}/start",response_model=UserActionOut)
def start(action_id:str,current_user:CurrentUser,db:DbSession):
 action=db.get(ClimateAction,action_id)
 if not action or not action.active: raise HTTPException(404,"Action not found")
 record=UserAction(user_id=current_user.id,action_id=action.id); db.add(record); db.commit(); db.refresh(record); return record
@router.post("/{action_id}/complete",response_model=CompletionOut)
def complete(action_id:str,current_user:CurrentUser,db:DbSession):
 action=db.get(ClimateAction,action_id)
 if not action or not action.active: raise HTTPException(404,"Action not found")
 record=db.scalar(select(UserAction).where(UserAction.user_id==current_user.id,UserAction.action_id==action.id).order_by(UserAction.created_at.desc()))
 if not record: record=UserAction(user_id=current_user.id,action_id=action.id); db.add(record); db.flush()
 if record.status=="completed": return CompletionOut(**UserActionOut.model_validate(record).model_dump(),xp=current_user.xp,current_streak=current_user.current_streak,longest_streak=current_user.longest_streak)
 record.status="completed"; record.completed_at=datetime.now(timezone.utc); record.xp_awarded=action.xp_reward; record.estimated_co2e_kg_awarded=action.estimated_co2e_kg or Decimal("0"); current_user.xp+=action.xp_reward; today=date.today()
 if current_user.last_action_date!=today:
  current_user.current_streak=current_user.current_streak+1 if current_user.last_action_date==date.fromordinal(today.toordinal()-1) else 1; current_user.longest_streak=max(current_user.longest_streak,current_user.current_streak); current_user.last_action_date=today
 db.commit(); db.refresh(record); db.refresh(current_user); return CompletionOut(**UserActionOut.model_validate(record).model_dump(),xp=current_user.xp,current_streak=current_user.current_streak,longest_streak=current_user.longest_streak)
