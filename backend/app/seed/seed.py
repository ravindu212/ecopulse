from sqlalchemy import select
from app.db import SessionLocal
from app.models.action import ClimateAction

ACTIONS = [("Walk or cycle a short journey", "walk-cycle-short", "transport", "Replace one short motor trip with walking or cycling.", "easy", "medium", 0.4, 50), ("Use public transport for one trip", "public-transport-trip", "transport", "Choose public transport where practical.", "easy", "medium", 0.3, 50), ("Combine errands into one journey", "combine-errands", "transport", "Plan errands to avoid extra trips.", "medium", "medium", 0.5, 80), ("Share a ride when practical", "share-a-ride", "transport", "Carpool when public transport is not practical.", "medium", "medium", 0.4, 80), ("Switch off unused devices", "switch-off-devices", "energy", "Turn off idle lights and electronics today.", "easy", "low", 0.1, 50), ("Reduce AC use for one hour", "reduce-ac", "energy", "Use ventilation or a fan where comfortable.", "medium", "medium", 0.2, 80), ("Use natural light", "use-natural-light", "energy", "Work near daylight when practical.", "easy", "low", None, 40), ("Unplug idle electronics", "unplug-idle-electronics", "energy", "Unplug chargers and devices not in use.", "easy", "low", 0.1, 50), ("Choose a plant-based meal", "plant-based-meal", "food", "Try one lower-impact meal this week.", "easy", "medium", 0.4, 50), ("Plan meals before shopping", "plan-meals", "food", "Plan portions and groceries to reduce waste.", "medium", "medium", 0.2, 80), ("Use leftovers", "use-leftovers", "food", "Make one meal from leftovers.", "easy", "low", 0.2, 50), ("Choose seasonal food", "choose-seasonal-food", "food", "Pick a seasonal option when available.", "medium", "low", None, 70), ("Carry a reusable bottle", "reusable-bottle", "waste", "Bring a bottle instead of buying a disposable drink.", "easy", "low", 0.1, 50), ("Avoid one single-use item", "avoid-single-use", "waste", "Refuse one unnecessary disposable item.", "easy", "low", 0.1, 50), ("Separate recyclable waste", "separate-recycling", "waste", "Sort recyclable waste where facilities exist.", "medium", "medium", 0.2, 80), ("Repair or reuse one item", "repair-reuse", "waste", "Repair or reuse before replacing something.", "hard", "high", None, 130)]

def seed() -> None:
    with SessionLocal() as db:
        for title, slug, category, description, difficulty, impact, estimate, xp in ACTIONS:
            if db.scalar(select(ClimateAction).where(ClimateAction.slug == slug)) is None:
                db.add(ClimateAction(title=title, slug=slug, category=category, description=description, why_it_matters=None, difficulty=difficulty, impact_level=impact, estimated_co2e_kg=estimate, xp_reward=xp, recommendation_tags=[]))
        db.commit()

if __name__ == "__main__": seed()
