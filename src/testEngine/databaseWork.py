from src.database.databaseUse import session_factory
from src.profile.models import Accreditation
from sqlalchemy import select
from src.testEngine.schemas import Direction
from src.testEngine.models import Question, Answer

def get_direction(acc_id, user_id) -> str:
    with session_factory() as session:
        stmt = (
            select(Accreditation.direction)
            .where(Accreditation.user_id == user_id and Accreditation.uid == acc_id)
        )
        direction = session.scalars(stmt).one_or_none()
        if direction is None:
            raise ValueError("Accreditation not found")
        return direction

def get_questions_by_direction(direction: Direction) -> list[Question]:
    direction = Direction(direction)
    with session_factory() as session:
        stmt = (
            select(Question)
            .where(Question.direction == direction)
        )
        questions = list(session.scalars(stmt).all())
        if questions is None:
            raise ValueError("Questions not found")
        return questions
