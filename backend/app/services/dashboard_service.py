from decimal import Decimal
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from app.models.action import ClimateAction, UserAction
from app.models.assessment import Assessment
from app.models.user import User
def summary(db:Session,user:User):
 assessment=db.scalar(select(Assessment).where(Assessment.user_id==user.id).order_by(Assessment.created_at.desc()).limit(1)); completed=UserAction.status=="completed"
 count,total=db.execute(select(func.count(UserAction.id),func.coalesce(func.sum(UserAction.estimated_co2e_kg_awarded),0)).where(UserAction.user_id==user.id,completed)).one()
 recent=list(db.scalars(select(UserAction).options(joinedload(UserAction.action)).where(UserAction.user_id==user.id,completed).order_by(UserAction.completed_at.desc()).limit(5)))
 rec=[]
 if assessment:
  scores={"transport":assessment.transport_score,"energy":assessment.energy_score,"food":assessment.food_score,"waste":assessment.waste_score}; cats=sorted(scores,key=lambda c:(scores[c],c)); actions=list(db.scalars(select(ClimateAction).where(ClimateAction.active.is_(True)).order_by(ClimateAction.title)))
  for cat in cats:
   rec.extend(a for a in actions if a.category==cat and a not in rec)
   if len(rec)>=3: break
  rec=rec[:3]
 return assessment,count,Decimal(total),recent,rec
