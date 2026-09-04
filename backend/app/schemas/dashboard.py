from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
class DashboardAction(BaseModel): id:UUID; title:str; category:str; difficulty:str; xp_reward:int; recommendation_reason:str
class RecentActivity(BaseModel): title:str; category:str; completed_at:datetime; xp_awarded:int; estimated_co2e_kg_awarded:float
class DashboardOut(BaseModel):
 name:str; xp:int; current_streak:int; longest_streak:int; climate_score:int|None; category_scores:dict[str,int]|None; lowest_category:str|None; assessment_date:datetime|None; estimated_co2e_avoided:float; completed_action_count:int; recent_activity:list[RecentActivity]; recommendations:list[DashboardAction]
