from src.database.databaseUse import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, CheckConstraint, DateTime, ForeignKey, Index, String, UniqueConstraint, func
from src.testEngine.schemas import Direction
from datetime import datetime
import uuid
from enum import IntEnum, StrEnum


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

class AttemptStatus(StrEnum):
    in_progress = "in_progress"
    finished = "finished"


class Attempt(Base):
    """Одно прохождение теста пользователем."""
    __tablename__ = "attempts"
    __table_args__ = (
        Index("ix_attempts_user_id", "user_id"),
    )

    attempt_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("User_info.uid", ondelete="CASCADE"))
    accreditation_id: Mapped[uuid.UUID | None] = mapped_column()

    # Параметры, с которыми собирался тест
    direction: Mapped[str] = mapped_column()
    skill: Mapped[str] = mapped_column()
    target: Mapped[int] = mapped_column()          
    self_rating: Mapped[int] = mapped_column()

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    score: Mapped[float | None] = mapped_column()

    questions: Mapped[list["AttemptQuestion"]] = relationship(
        back_populates="attempt",
        cascade="all, delete-orphan",
        order_by="AttemptQuestion.position",
    )


class AttemptQuestion(Base):
    """Снимок вопроса в конкретной попытке."""
    __tablename__ = "attempt_questions"
    __table_args__ = (
        UniqueConstraint("attempt_id", "position", name="uq_attempt_question_position"),
        Index("ix_attempt_questions_question_id", "question_id"),
        CheckConstraint("difficulty BETWEEN 1 AND 3", name="ck_attempt_questions_difficulty"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("attempts.attempt_id", ondelete="CASCADE")
    )
    # Ссылка на оригинал; если вопрос удалят из банка, снимок останется
    question_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("questions.question_id", ondelete="SET NULL")
    )
    position: Mapped[int] = mapped_column()         # номер вопроса в тесте, с 1

    # Снимок содержимого на момент теста
    question_text: Mapped[str] = mapped_column()
    difficulty: Mapped[int] = mapped_column()
    direction: Mapped[str] = mapped_column()
    skill: Mapped[str] = mapped_column()

    is_correct: Mapped[bool | None] = mapped_column()  # заполняется при проверке

    attempt: Mapped["Attempt"] = relationship(back_populates="questions")
    answers: Mapped[list["AttemptAnswer"]] = relationship(
        back_populates="attempt_question",
        cascade="all, delete-orphan",
        order_by="AttemptAnswer.position",
    )


class AttemptAnswer(Base):
    """Снимок варианта ответа и отметка, выбрал ли его пользователь."""
    __tablename__ = "attempt_answers"
    __table_args__ = (
        UniqueConstraint("attempt_question_id", "position", name="uq_attempt_answer_position"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('attempts.attempt_id', ondelete="CASCADE")
    )
    attempt_question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("attempt_questions.id", ondelete="CASCADE")
    )
    answer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("answers.answer_id", ondelete="SET NULL")
    )
    position: Mapped[int] = mapped_column()         # порядок показа варианта

    answer_text: Mapped[str] = mapped_column()
    is_true: Mapped[bool] = mapped_column()
    is_selected: Mapped[bool] = mapped_column(default=False)

    attempt_question: Mapped["AttemptQuestion"] = relationship(back_populates="answers")



    