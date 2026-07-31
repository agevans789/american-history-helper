import asyncio
from sqlalchemy import text
from api.database import async_session, Base, engine

try:
    from api.routes import discover 
except ImportError:
    pass

async def seed_graph_database():
    print("Initializing local SQLite history discovery database...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with async_session() as session:
        print("Clearing historical table data...")
        try:
            await session.execute(text("DELETE FROM relationships;"))
            await session.execute(text("DELETE FROM historical_entries;"))
        except Exception as e:
            print(f"Bypassing safe truncate check: {e}")
        
        print("Injecting primary historical nodes...")
        entries_sql = text("""
            INSERT INTO historical_entries (entry_id, title, content, historical_era) VALUES
            (1, 'George Washington', 'First President of the United States and Commander of the Continental Army during the American Revolutionary War.', 'Revolutionary War Era'),
            (2, 'The Stamp Act of 1765', 'A direct tax imposed by British Parliament on printed materials in the American colonies, sparking early unified colonial resistance.', 'Revolutionary War Era'),
            (3, 'The Boston Tea Party', 'A political protest by the Sons of Liberty in Boston where colonists frustrated at British taxation without representation dumped tea into the harbor.', 'Revolutionary War Era'),
            (4, 'The Declaration of Independence', 'The formal statement adopted by the Second Continental Congress declaring the thirteen colonies free from Great Britain.', 'Revolutionary War Era'),
            (5, 'The Battles of Lexington and Concord', 'The opening military engagements of the Revolutionary War, marking the outbreak of armed structural conflict.', 'Revolutionary War Era');
        """)
        await session.execute(entries_sql)
        
        print("Building structural discovery graph connections...")
        relationships_sql = text("""
            INSERT INTO relationships (source_entry_id, target_entry_id, weight, relationship_type) VALUES
            (2, 3, 0.90, 'Causation'),     -- Stamp Act caused the Boston Tea Party
            (3, 5, 0.95, 'Escalation'),    -- Boston Tea Party escalated into Lexington & Concord
            (5, 4, 0.85, 'Aftermath'),     -- Battles resulted in the Declaration of Independence
            (4, 1, 0.99, 'Biography');     -- Declaration relates directly back to George Washington
        """)
        await session.execute(relationships_sql)
        
        await session.commit()
        print("🎉 Success! 5 historical nodes and discovery graph paths have been fully seeded into SQLite.")

if __name__ == "__main__":
    asyncio.run(seed_graph_database())
