"""
SQLAlchemy-based key-value store for Minecraft GPT project.
Implements put and search methods with SQLite backend.
"""

import json
import time
from typing import Any, Literal

from sqlalchemy import (
    JSON,
    Column,
    Float,
    Integer,
    String,
    Text,
    and_,
    create_engine,
    func,
    or_,
    select,
)
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    writer = Column(String, index=True)
    writer_type = Column(String, index=True)
    player_id = Column(String, index=True)
    message = Column(Text)
    created_at = Column(Float, default=lambda: time.time())
    updated_at = Column(
        Float, default=lambda: time.time(), onupdate=lambda: time.time()
    )


class SQLAlchemyStore:
    def __init__(self, db_path="sqlite:///chroma_langchain_db/chroma.sqlite3"):
        self.engine = create_engine(db_path, echo=False, future=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, future=True)

    def put_message(
        self, writer: str, writer_type: str, message: str, player_id: str | None = None
    ) -> None:
        now = time.time()
        with self.Session() as session:
            msg = Message(
                writer=writer,
                writer_type=writer_type,
                player_id=player_id,
                message=message,
                created_at=now,
                updated_at=now,
            )
            session.add(msg)
            session.commit()

    def get_last_messages(self, limit: int = 10) -> list[dict[str, Any]]:
        with self.Session() as session:
            stmt = select(Message).order_by(Message.created_at.desc()).limit(limit)
            results = session.execute(stmt).scalars().all()
            return [
                {
                    "writer": m.writer,
                    "writer_type": m.writer_type,
                    "player_id": m.player_id,
                    "message": m.message,
                    "created_at": m.created_at,
                    "updated_at": m.updated_at,
                }
                for m in results
            ]

    def get_last_messages_for_player(
        self, player_id: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        with self.Session() as session:
            stmt = (
                select(Message)
                .where(or_(Message.writer == player_id, Message.player_id == player_id))
                .order_by(Message.created_at.desc())
                .limit(limit)
            )
            results = session.execute(stmt).scalars().all()
            return [
                {
                    "writer": m.writer,
                    "writer_type": m.writer_type,
                    "player_id": m.player_id,
                    "message": m.message,
                    "created_at": m.created_at,
                    "updated_at": m.updated_at,
                }
                for m in results
            ]
