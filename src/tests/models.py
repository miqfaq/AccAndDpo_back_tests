from pydantic import BaseModel, Field
from sqlalchemy import ForeignKey
from typing import Optional
from fastapi import Depends
from src.database.databaseUse import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
import uuid


class Tests(Base):
    __tablename__ = "Tests"
    uid: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    testName: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    userUid: Mapped[Optional[str]] = mapped_column(
        ForeignKey("User_info.uid", ondelete="CASCADE"), nullable=True
    )
    questions: Mapped[List["Questions"]] = relationship(
        back_populates="test", cascade="all, delete-orphan"
    )

class Questions(Base):
    __tablename__='Questions'
    uid: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    testId: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('Tests.uid', ondelete="CASCADE")
    )
    question_text: Mapped[str] = mapped_column()
    test: Mapped["Tests"] = relationship(back_populates="questions")
    answers: Mapped[List["Answers"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )
    

class Answers(Base):
    __tablename__="Answers"
    uid: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    questionId: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('Questions.uid', ondelete="CASCADE")
    )
    answer_text: Mapped[str] = mapped_column()
    answer_is_true: Mapped[bool] = mapped_column(default=True)
    question: Mapped["Questions"] = relationship(back_populates="answers")


class PaginationParams(BaseModel):
    limit: int = Field(5, ge=5, le=100)
    offset: int = Field(0)
    
