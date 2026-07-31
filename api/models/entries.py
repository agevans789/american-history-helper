from sqlalchemy import Column, Integer, String, Text, Date, Numeric, ForeignKey, UniqueConstraint
from api.database import Base

class HistoricalEntry(Base):
    __tablename__ = "historical_entries"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    historical_era = Column(String(100))
    date_occurred = Column(Date)

class Relationship(Base):
    __tablename__ = "relationships"

    relationship_id = Column(Integer, primary_key=True, index=True)
    source_entry_id = Column(Integer, ForeignKey('historical_entries.id', ondelete='CASCADE'))
    target_entry_id = Column(Integer, ForeignKey('historical_entries.id', ondelete='CASCADE'))
    weight = Column(Numeric(3, 2), default=1.0)
    relationship_type = Column(String(50))

    __table_args__ = (
        UniqueConstraint('source_entry_id', 'target_entry_id', name='unique_source_target'),
    )