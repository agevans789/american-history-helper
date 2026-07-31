from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, func
from api.database import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SearchHistory(Base):
    __tablename__ = "search_history"
    search_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'))
    search_query = Column(String(255), nullable=False)
    search_date = Column(DateTime(timezone=True), server_default=func.now())

class SavedItem(Base):
    __tablename__ = "saved_items"
    saved_item_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'))
    entry_id = Column(Integer, ForeignKey('historical_entries.entry_id', ondelete='CASCADE'))
    saved_date = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'entry_id', name='unique_user_entry_save'),
    )