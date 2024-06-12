from sqlalchemy import Integer, DateTime, String, func, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())


class Exchange(Base):
    __tablename__ = 'new_exchange'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(Integer, unique=True)
    exchanger: Mapped[str] = mapped_column(String(50))
    usdt: Mapped[float] = mapped_column(Float(2), nullable=True)
    rub: Mapped[float] = mapped_column(Float(2), nullable=True)
