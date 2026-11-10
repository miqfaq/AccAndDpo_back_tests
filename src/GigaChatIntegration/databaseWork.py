from src.database.databaseUse import session_factory
from sqlalchemy import select
from src.testEngine.models import Attempt, AttemptAnswer, AttemptQuestion
from src.profile.models import Accreditation



async def get_acc_context(acc_id):
    async with session_factory() as session:
        stmt = (select(Accreditation)
                .where(Accreditation.uid == acc_id))
        res = await session.execute(stmt)
        return res.scalars().all()

async def get_att_context(att_id) -> list[AttemptAnswer]: 
    async with session_factory() as session:
        statement = (
            select(AttemptAnswer)
            .join(AttemptQuestion, AttemptAnswer.attempt_question_id == AttemptQuestion.id)
            .where(AttemptQuestion.attempt_id == att_id)
        )
        
        # .scalars().all() вернет плоский список [AttemptAnswer, AttemptAnswer, ...]
        res = await session.execute(statement)
        return list(res.scalars().all())