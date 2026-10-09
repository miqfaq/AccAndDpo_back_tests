import uuid
from src.database.databaseUse import Base
from sqlalchemy.orm import Mapped, mapped_column



class UserData(Base):
    __tablename__ = 'user_auth'
    uid: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    hash_password: Mapped[str] = mapped_column()
    role: Mapped[str] = mapped_column( default='user')

class UserRole():
    admin = 'admin'
    user = 'user'
    guest = 'guest'