from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class Option:
    id: str
    label: str
    score: int


@dataclass(frozen=True)
class Question:
    id: str
    category: str
    text: str
    options: tuple[Option, ...]


def options(*values: tuple[str, str, int]) -> tuple[Option, ...]:
    return tuple(Option(*value) for value in values)


QUESTIONS: Final[tuple[Question, ...]] = (
    Question("T1", "transport", "What is your most common travel mode?", options(("walk_cycle", "Walk or cycle", 100), ("train", "Train", 85), ("bus", "Bus", 75), ("shared_car", "Shared car or ride", 55), ("motorcycle", "Motorcycle", 40), ("private_car", "Private car", 25))),
    Question("T2", "transport", "How often do you walk or cycle for short trips?", options(("almost_always", "Almost always", 100), ("often", "Often", 80), ("sometimes", "Sometimes", 60), ("rarely", "Rarely", 30), ("never", "Never", 10))),
    Question("T3", "transport", "How often do you use public transport when practical?", options(("almost_always", "Almost always", 100), ("often", "Often", 80), ("sometimes", "Sometimes", 60), ("rarely", "Rarely", 30), ("never", "Never", 10))),
    Question("E1", "energy", "Do you turn off lights and devices when not needed?", options(("always", "Always", 100), ("usually", "Usually", 80), ("sometimes", "Sometimes", 55), ("rarely", "Rarely", 25))),
    Question("E2", "energy", "How often do you use air conditioning for long periods?", options(("rarely_never", "Rarely or never", 100), ("occasionally", "Occasionally", 75), ("several_days", "Several days a week", 45), ("daily", "Daily for long periods", 20))),
    Question("E3", "energy", "Do you intentionally use energy-saving settings?", options(("frequently", "Frequently", 100), ("sometimes", "Sometimes", 65), ("rarely", "Rarely", 30), ("not_sure", "Not sure", 50))),
    Question("F1", "food", "How often do you eat high-impact meat meals?", options(("rarely", "Rarely", 100), ("one_two", "1 to 2 times a week", 80), ("three_four", "3 to 4 times a week", 55), ("most_days", "Most days", 30))),
    Question("F2", "food", "How often is food thrown away in your meals or household?", options(("almost_never", "Almost never", 100), ("occasionally", "Occasionally", 75), ("sometimes", "Sometimes", 50), ("often", "Often", 20))),
    Question("F3", "food", "Do you choose local, seasonal, or lower-waste food options?", options(("often", "Often", 100), ("sometimes", "Sometimes", 65), ("rarely", "Rarely", 30))),
    Question("W1", "waste", "How often do you use reusable bottles, bags, or containers?", options(("almost_always", "Almost always", 100), ("often", "Often", 80), ("sometimes", "Sometimes", 55), ("rarely", "Rarely", 25))),
    Question("W2", "waste", "Do you separate recyclable waste where facilities are available?", options(("consistently", "Consistently", 100), ("sometimes", "Sometimes", 60), ("rarely", "Rarely", 25), ("unavailable", "Facilities are unavailable", 50))),
    Question("W3", "waste", "How often do you avoid unnecessary single-use items?", options(("almost_always", "Almost always", 100), ("often", "Often", 80), ("sometimes", "Sometimes", 55), ("rarely", "Rarely", 25))),
)

QUESTION_BY_ID = {question.id: question for question in QUESTIONS}
CATEGORY_ORDER: Final = ("transport", "energy", "food", "waste")


def public_questions() -> list[dict[str, object]]:
    return [{"id": q.id, "category": q.category, "text": q.text, "options": [{"id": o.id, "label": o.label} for o in q.options]} for q in QUESTIONS]


def calculate_scores(answers: dict[str, str]) -> dict[str, int | str]:
    expected_ids = set(QUESTION_BY_ID)
    supplied_ids = set(answers)
    if supplied_ids != expected_ids:
        missing = sorted(expected_ids - supplied_ids)
        unknown = sorted(supplied_ids - expected_ids)
        details = []
        if missing: details.append(f"Missing answers: {', '.join(missing)}")
        if unknown: details.append(f"Unknown questions: {', '.join(unknown)}")
        raise ValueError("; ".join(details))

    category_values: dict[str, list[int]] = {category: [] for category in CATEGORY_ORDER}
    for question_id, option_id in answers.items():
        question = QUESTION_BY_ID[question_id]
        option = next((option for option in question.options if option.id == option_id), None)
        if option is None:
            raise ValueError(f"Invalid answer for {question_id}")
        category_values[question.category].append(option.score)

    scores = {category: round(sum(values) / len(values)) for category, values in category_values.items()}
    scores["overall_score"] = round(sum(scores[category] for category in CATEGORY_ORDER) / len(CATEGORY_ORDER))
    scores["lowest_category"] = min(CATEGORY_ORDER, key=lambda category: scores[category])
    return scores
