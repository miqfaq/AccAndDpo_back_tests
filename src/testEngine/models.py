from src.database.databaseUse import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from typing import Optional
import uuid
from datetime import datetime

class Attempts(Base):
    __tablename__ = "Attempts"
    uid: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    testId: Mapped[uuid.UUID] = mapped_column(ForeignKey("Tests.uid", ondelete="CASCADE"))
    userUid: Mapped[uuid.UUID] = mapped_column(ForeignKey("User_info.uid", ondelete="CASCADE"))
    started_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    finished_at: Mapped[Optional[datetime]] = mapped_column()
    score: Mapped[Optional[float]] = mapped_column()