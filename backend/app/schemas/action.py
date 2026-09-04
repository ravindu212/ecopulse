from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict
class ActionOut(BaseModel):
 model_config=ConfigDict(from_attributes=True)
 id:UUID; title:str; slug:str; category:str; description:str; why_it_matters:str|None; difficulty:str; impact_level:str; estimated_co2e_kg:Decimal|None; xp_reward:int
class RecommendedAction(ActionOut): recommendation_reason:str
class UserActionOut(BaseModel):
 model_config=ConfigDict(from_attributes=True)
 id:UUID; action_id:UUID; status:str; completed_at:datetime|None; xp_awarded:int; estimated_co2e_kg_awarded:Decimal
class CompletionOut(UserActionOut): xp:int; current_streak:int; longest_streak:int
