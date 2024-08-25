from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func, ForeignKey


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Profile(Base):
    __tablename__ = 'profile'

    id_all: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    gender: Mapped[str] = mapped_column(String(8), nullable=False)
    age: Mapped[str] = mapped_column(String(30), nullable=False)
    country: Mapped[str] = mapped_column(String(30), nullable=False)
    city: Mapped[str] = mapped_column(String(30), nullable=False)
    photography: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(String(255), default='')
    count_grades: Mapped[int] = mapped_column(default=0)
    all_grades: Mapped[int] = mapped_column(default=0)
    wanted_gender: Mapped[str] = mapped_column(String(20), default='Без разницы 👫')
    ban: Mapped[str] = mapped_column(String(5), default='lock')


class NewGrade(Base):
    __tablename__ = 'newgrades'

    id_all: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_user: Mapped[str] = mapped_column(String(40), default=None)
    liked_id: Mapped[str] = mapped_column(ForeignKey('profile.id', ondelete='CASCADE'))
    new_count_grades: Mapped[int] = mapped_column(default=0)
    grade: Mapped[int] = mapped_column(default=None)
    user_name: Mapped[str] = mapped_column(String(80), default='')

    profile: Mapped['Profile'] = relationship(backref='newgrades')


class Report(Base):
    __tablename__ = 'reports'

    id_all: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id: Mapped[str] = mapped_column(String(40))
    report_id: Mapped[str] = mapped_column(String(40))
    report: Mapped[str] = mapped_column(String(255))

