from src.database.databaseUse import session_factory
from sqlalchemy import select
from src.testEngine.models import Attempt, AttemptAnswer, AttemptQuestion
from src.profile.models import Accreditation



def get_acc_context(acc_id):
    with session_factory() as session:
        stmt = (select(Accreditation)
                .where(Accreditation.uid == acc_id))
        return session.scalars(stmt).all()

def get_att_context(att_id) -> list[AttemptAnswer]: 
    with session_factory() as session:
        statement = (
            select(AttemptAnswer)
            .join(AttemptQuestion, AttemptAnswer.attempt_question_id == AttemptQuestion.id)
            .where(AttemptQuestion.attempt_id == att_id)
        )
        
        # .scalars().all() вернет плоский список [AttemptAnswer, AttemptAnswer, ...]
        return list(session.scalars(statement).all())