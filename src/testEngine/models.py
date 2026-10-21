from src.database.databaseUse import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.testEngine.schemas import Direction
import uuid


class Answer(Base):
    __tablename__ = 'answers'
    answer_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    answer_text: Mapped[str] = mapped_column()
    is_true: Mapped[bool] = mapped_column()
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.question_id", ondelete="CASCADE")
    )
    

class Question(Base):
    __tablename__= 'questions'
    question_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    question_text: Mapped[str] = mapped_column()
    difficulty: Mapped[int] = mapped_column(default=1)
    direction: Mapped[str] = mapped_column(default=Direction.default)
    skill: Mapped[str] = mapped_column(default='default')
    ability: Mapped[str] = mapped_column(default='default')
    answers: Mapped[list["Answer"]] = relationship(
        cascade="all, delete-orphan"
    )
