from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:roshan@localhost:5433/Bug_Tracker')
try:
    with engine.connect() as conn:
        conn.execute(text('DROP TABLE IF EXISTS alembic_version'))
        conn.commit()
        print("✅ Deleted alembic_version table - ready for fresh migration")
except Exception as e:
    print(f"❌ Error: {e}")
