from src.database.databaseUse import session_factory
from src.profile.models import Accreditation
from sqlalchemy import select

def get_direction(acc_id, user_id):
    with session_factory() as session:
        stmt = (
            select(Accreditation.direction)
            .where(Accreditation.user_id == user_id and Accreditation.uid == acc_id)
        )
        direction = session.scalars(stmt).one_or_none()
        if direction is None:
            raise ValueError("Accreditation not found")
        return direction
