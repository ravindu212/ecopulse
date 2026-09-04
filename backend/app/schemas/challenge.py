from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
class ChallengeActionItem(BaseModel): id:UUID; title:str; slug:str; category:str; difficulty:str; sort_order:int
class ChallengeOut(BaseModel): id:UUID; title:str; slug:str; description:str; active:bool; required_actions:list[ChallengeActionItem]
class JoinedChallengeOut(BaseModel): challenge_id:UUID; title:str; slug:str; status:str; joined_at:datetime; completed_at:datetime|None; completed_required_actions:int; total_required_actions:int; progress_percent:float
