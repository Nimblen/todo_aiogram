from sqlalchemy import Text, DateTime, func, Boolean, String, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

class User(Base):
    __tablename__ = "user"
    user_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    username: Mapped[str] = mapped_column(String, nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

class Task(Base):
    __tablename__ = "task"
    task: Mapped[str] = mapped_column(Text)
    routine: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.date())
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.user_id"))


class Word(Base):
        __tablename__ = "word"
        rus_word: Mapped[str] = mapped_column(String(20))
        eng_word: Mapped[str] = mapped_column(String(20))
        description: Mapped[str] = mapped_column(String(200), nullable=True)



# class Task(Base):
#     __tablename__ = 'task'
#     task = Column(Text)
#     routine = Column(Boolean, default=False)
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
