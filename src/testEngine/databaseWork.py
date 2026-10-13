from src.database.databaseUse import session_factory
from src.testgroup.models import Tests, Questions
from src.testEngine.schemas import SubmitTest, TestPublic, TestResult, QuestionResult
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import uuid


def get_test_for_passing(test_uid: uuid.UUID):
    with session_factory() as session:
        stmt = (
            select(Tests)
            .where(Tests.uid == test_uid)
            .options(selectinload(Tests.questions).selectinload(Questions.answers))
        )
        return session.scalar(stmt)

def check_test(test_uid: uuid.UUID, submit: SubmitTest) -> TestResult:
    with session_factory() as session:
        stmt = (
            select(Questions)
            .where(Questions.testId == test_uid)
            .options(selectinload(Questions.answers))
        )
        questions = session.scalars(stmt).all()

        user_map = {a.question_id: set(a.answer_ids) for a in submit.answers}

        details = []
        correct_count = 0
        for q in questions:
            right = {a.uid for a in q.answers if a.answer_is_true}
            chosen = user_map.get(q.uid, set())
            ok = chosen == right
            correct_count += ok
            details.append(QuestionResult(
                question_id=q.uid,
                is_correct=ok,
                correct_answer_ids=list(right),
            ))

        total = len(questions)
        return TestResult(
            total=total,
            correct=correct_count,
            percent=round(correct_count / total * 100, 1) if total else 0.0,
            details=details,
        )

    