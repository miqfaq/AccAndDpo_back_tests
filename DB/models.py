import uuid

from .databaseUse import Base
from sqlalchemy.orm import Mapped, mapped_column



class UserData(Base):
    __tablename__ = 'user_auth'
    uid: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column()
    hash_password: Mapped[str] = mapped_column()