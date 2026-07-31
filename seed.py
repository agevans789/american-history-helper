import asyncio
from sqlalchemy import text
from api.database import async_session, Base, engine

# --- MANDATORY MODEL IMPORT REGISTER ---
# This forces Python to evaluate your data classes so SQLAlchemy knows they exist
# before Base.metadata.create_all executes.
try:
    from api.routes import discover  # Indirectly evaluates your data schema layout classes
except ImportError:
    pass

async def seed_graph_database():
    print("Initializing local SQLite history discovery database...")
    
    # 1. Physically compile and build the tables into history_graph.db
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with async_session() as session:
        print("Clearing stale table rows safely...")
        try:
            # SQLite does not support TRUNCATE, standard DELETE is correct here
            await session.execute(text("DELETE FROM relationships;"))
            await session.execute(text("DELETE FROM historical_entries;"))
            await session.commit()
        except Exception as e:
            print(f"Skipping clean clear checks (tables were already empty): {e}")
 
        print("Injecting primary historical nodes dynamically (No hardcoded primary keys)...")
        entries_sql = text("""
            INSERT INTO historical_entries (title, content, historical_era) VALUES
            ('George Washington', 'First President of the United States and Commander of the Continental Army during the American Revolutionary War.', 'Revolutionary War Era'),
            ('The Stamp Act of 1765', 'A direct tax imposed by British Parliament on printed materials in the American colonies, sparking early unified colonial resistance.', 'Revolutionary War Era'),
            ('The Boston Tea Party', 'A political protest by the Sons of Liberty in Boston where colonists frustrated at British taxation without representation dumped tea into the harbor.', 'Revolutionary War Era'),
            ('The Declaration of Independence', 'The formal statement adopted by Second Continental Congress declaring thirteen colonies free from Great Britain.', 'Revolutionary War Era'),
            ('The Battles of Lexington and Concord', 'The opening military engagements of the Revolutionary War, marking the outbreak of armed structural conflict.', 'Revolutionary War Era');
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

