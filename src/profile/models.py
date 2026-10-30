from src.database.databaseUse import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship, deferred
from sqlalchemy import ForeignKey, String, LargeBinary, CheckConstraint
from typing import Optional
import uuid

class UserData(Base):
    __tablename__ = 'User_info'
    uid: Mapped[str] = mapped_column(
        ForeignKey("user_auth.uid", ondelete="CASCADE"), 
        primary_key=True,
    )
    username: Mapped[str] = mapped_column(String(20), unique=True)
    firstName: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    lastName: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    midName: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    position: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    area: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    target_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    photo: Mapped[Optional[bytes]] = deferred(mapped_column(LargeBinary, nullable=True))
    accreditations: Mapped[list["Accreditation"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
        
class Accreditation(Base):
    __tablename__ ="accreditation_session"
    uid: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("User_info.uid", ondelete="CASCADE"), 
        index=True
                )
    direction: Mapped[str] = mapped_column()
    skill: Mapped[str] = mapped_column()
    target: Mapped[int] = mapped_column()
    self_rating: Mapped[int] = mapped_column(default=1)
    rating: Mapped[int] = mapped_column(default=1)
    abilitys: Mapped[list["Ability"]] = relationship(
        cascade="all, delete-orphan"
    )
    user: Mapped["UserData"] = relationship(
        back_populates="accreditations"
    )
    __table_args__ = (
        CheckConstraint("target >= 1 and target <= 100", name="check_target"),
        CheckConstraint("self_rating >= 1 and self_rating <= 100", name="check_self_rating"),
        CheckConstraint("rating >= 1 and rating <= 100", name="checkrating")
    )
    
class Ability(Base):
    __tablename__='ability'
    uid: Mapped[uuid.UUID] = mapped_column( primary_key=True, default=uuid.uuid4)
    accreditation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accreditation_session.uid", ondelete="CASCADE"),
        index=True
    )
    name: Mapped[str] = mapped_column()


