from typing import Optional
from sqlalchemy import Boolean, DateTime, String, text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from datetime import datetime, timezone
from .base import Base


# default - это значение по умолчанию, которое устанавливается на уровне Python/SQLAlchemy
# server_default - это значение по умолчанию, которое устанавливается на уровне базы данных (в SQL)


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(500))
    is_completed: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow,  # Используйте `utcnow` без часового пояса
        nullable=False,
    )
