from src.testgroup.models import Tests, Questions, Answers
from src.testgroup.schemas import TestUpdateSchema, TestCreateSchema, QuestionCreateSchema, AnswerCreateSchema
from sqlalchemy import select, update, delete
from src.database.databaseUse import session_factory
from typing import List
import uuid


def add_test(test: TestCreateSchema, questions: List[QuestionCreateSchema], useruid):
    with session_factory() as session:
        test_in = Tests(uid = uuid.uuid4(),testName=test.testName, description=test.description, userUid = useruid)

        for q in questions:
            question = Questions(uid = uuid.uuid4(), question_text=q.question_text)
            question.answers = [
                Answers(uid = uuid.uuid4(), answer_text=a.answer_text, answer_is_true=a.answer_is_true)
                for a in q.answers
            ]
            test_in.questions.append(question)

        session.add(test_in)   # каскадом добавятся вопросы и ответы
        session.commit()
        session.refresh(test_in)
        return test_in

def get_tests():
    with session_factory() as session:
        stmt = (
            select(Tests)
        )
        test_all = session.execute(stmt).scalars().all()
        return test_all

def get_tests_UserId(user_id: str):
    with session_factory() as session:
        stmt =(
            select(Tests)
            .where(Tests.userUid == user_id)
        )
        tests_uid = session.execute(stmt).scalars().all()
        return tests_uid

def get_test_TestId(test_id: str):
    with session_factory() as session:
        stmt =(
            select(Tests)
            .where(Tests.uid == test_id)
        )
        tests_uid = session.execute(stmt).scalar()
        return tests_uid

def update_test_TestId(test_id: str, data: TestUpdateSchema):
    with session_factory() as session:
        test = session.get(Tests, test_id)
        if test is None:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(test, field, value)

        session.commit()
        session.refresh(test)
        return test

def delete_test(userId, testId: str):
    with session_factory() as session:
            stmt =(
                delete(Tests)
                .where(Tests.uid == testId, Tests.userUid == userId)
            )
            session.execute(stmt)
            session.commit()
