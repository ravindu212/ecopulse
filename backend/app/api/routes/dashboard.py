from fastapi import APIRouter
from app.api.deps import CurrentUser, DbSession
from app.schemas.dashboard import DashboardOut,DashboardAction,RecentActivity
from app.services.dashboard_service import summary
router=APIRouter(prefix="/dashboard",tags=["dashboard"])
@router.get("",response_model=DashboardOut)
def dashboard(current_user:CurrentUser,db:DbSession):
 assessment,count,total,recent,rec=summary(db,current_user)
 return DashboardOut(name=current_user.name,xp=current_user.xp,current_streak=current_user.current_streak,longest_streak=current_user.longest_streak,climate_score=assessment.overall_score if assessment else None,category_scores={"transport":assessment.transport_score,"energy":assessment.energy_score,"food":assessment.food_score,"waste":assessment.waste_score} if assessment else None,lowest_category=assessment.lowest_category if assessment else None,assessment_date=assessment.created_at if assessment else None,estimated_co2e_avoided=total,completed_action_count=count,recent_activity=[RecentActivity(title=x.action.title,category=x.action.category,completed_at=x.completed_at,xp_awarded=x.xp_awarded,estimated_co2e_kg_awarded=x.estimated_co2e_kg_awarded) for x in recent],recommendations=[DashboardAction(id=x.id,title=x.title,category=x.category,difficulty=x.difficulty,xp_reward=x.xp_reward,recommendation_reason=f"Recommended because {x.category} was one of your lowest assessment categories.") for x in rec])
