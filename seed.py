import asyncio
from sqlalchemy import text
from api.database import async_session, engine

async def seed_graph_database():
    print("Initializing local SQLite history discovery database using raw schemas...")
    
    async with engine.begin() as conn:
        print("Enforcing strict SQLite foreign key parameters...")
        await conn.execute(text("PRAGMA foreign_keys = ON;"))
        
        print("Stamping raw table structures...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS historical_entries (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                historical_era TEXT NOT NULL
            );
        """))
  
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS relationships (
                relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_entry_id INTEGER NOT NULL,
                target_entry_id INTEGER NOT NULL,
                weight REAL NOT NULL,
                relationship_type TEXT NOT NULL,
                FOREIGN KEY (source_entry_id) REFERENCES historical_entries(entry_id) ON DELETE CASCADE,
                FOREIGN KEY (target_entry_id) REFERENCES historical_entries(entry_id) ON DELETE CASCADE
            );
        """))
        
    async with async_session() as session:
        print("Safely purging legacy data packets across relational trees...")
        await session.execute(text("DELETE FROM relationships;"))
        await session.execute(text("DELETE FROM historical_entries;"))
        
        await session.execute(text("DELETE FROM sqlite_sequence WHERE name IN ('historical_entries', 'relationships');"))
        
        print("Injecting primary historical nodes smoothly...")
        entries_sql = text("""
            INSERT INTO historical_entries (title, content, historical_era) VALUES
            ('George Washington', 'First President of the United States and Commander of the Continental Army during the American Revolutionary War.', 'Revolutionary War Era'),
            ('The Stamp Act of 1765', 'A direct tax imposed by British Parliament on printed materials in the American colonies, sparking early unified colonial resistance.', 'Revolutionary War Era'),
            ('The Boston Tea Party', 'A political protest by the Sons of Liberty in Boston where colonists frustrated at British taxation without representation dumped tea into the harbor.', 'Revolutionary War Era'),
            ('The Declaration of Independence', 'The formal statement adopted by the Second Continental Congress declaring the thirteen colonies free from Great Britain.', 'Revolutionary War Era'),
            ('The Battles of Lexington and Concord', 'The opening military engagements of the Revolutionary War, marking the outbreak of armed structural conflict.', 'Revolutionary War Era');
        """)
        await session.execute(entries_sql)
        
        print("Building structural graph connections using true sequence indexes...")
        relationships_sql = text("""
            INSERT INTO relationships (source_entry_id, target_entry_id, weight, relationship_type) VALUES
            (2, 3, 0.90, 'Causation'),     -- Stamp Act -> Boston Tea Party
            (3, 5, 0.95, 'Escalation'),    -- Boston Tea Party -> Lexington & Concord
            (5, 4, 0.85, 'Aftermath'),     -- Battles -> Declaration of Independence
            (4, 1, 0.99, 'Biography');     -- Declaration -> George Washington
        """)
        await session.execute(relationships_sql)
        
        await session.commit()
        print("🎉 Success! 5 historical nodes and discovery graph paths have been fully seeded into SQLite.")

if __name__ == "__main__":
    asyncio.run(seed_graph_database())

