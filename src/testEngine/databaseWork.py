from src.database.databaseUse import session_factory
from src.profile.models import Accreditation
from sqlalchemy import select
from src.testEngine.schemas import Direction, QuestionShcema
from src.testEngine.models import Question, Answer
from src.testEngine.testconstructor import FirstTest
import uuid

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

def getTest(userId: uuid.UUID, acc_id: uuid.UUID):
    with session_factory() as session:
        target = session.scalars(select(Accreditation.target).where(Accreditation.user_id == userId, Accreditation.uid == acc_id)).one()
        skill = session.scalars(select(Accreditation.skill).where(Accreditation.user_id == userId, Accreditation.uid == acc_id)).one()
        direction = session.scalars(select(Accreditation.direction).where(Accreditation.user_id == userId, Accreditation.uid == acc_id)).one()
        self_rating = session.scalars(select(Accreditation.self_rating).where(Accreditation.user_id == userId, Accreditation.uid == acc_id)).one()
        test = FirstTest(session=session, user_id=userId, direction=direction, skill=skill, target=target, self_rating=self_rating  )
        return test.build()

def addQuestion(question: QuestionShcema):
    with session_factory() as session:
        session.add(Question(
            question_text = question.question_text,
            difficulty = question.difficulty,
            direction = question.direction,
            skill = question.skill,
            ability = question.ability,
            answers = [
                Answer(answer_text = answer.answer_text.strip(), is_true=answer.is_true)
                for answer in question.answer_list
            ],
        ))
        session.commit()
