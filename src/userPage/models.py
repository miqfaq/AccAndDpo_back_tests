from src.database.databaseUse import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String
from typing import Optional

class UserData(Base):
    __tablename__ = 'User_info'
    uid: Mapped[str] = mapped_column(
        ForeignKey("user_auth.uid", ondelete="CASCADE"), 
        primary_key=True,
        autoincrement=False
    )
    username: Mapped[str] = mapped_column(String(20), unique=True)
    firstName: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    lastName: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    midName: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    completedTests: Mapped[Optional[int]] = mapped_column(default=0, nullable=True)
    totalTests: Mapped[Optional[int]] = mapped_column(default=0, nullable=True)
    abc_test_result: Mapped[Optional[str]] = mapped_column(default=0, nullable=True)


