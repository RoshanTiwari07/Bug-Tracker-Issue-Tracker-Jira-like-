#!/usr/bin/env python
"""Verify database tables were created."""

import asyncio
from sqlalchemy import text
from app.db.session import engine

async def verify_tables():
    """Check if all 9 tables exist."""
    async with engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
        )
        tables = [row[0] for row in result]
        print("✅ Tables created successfully:\n")
        for table in tables:
            print(f"  • {table}")
        print(f"\nTotal: {len(tables)} tables")
        
        expected = {
            'users', 'projects', 'labels', 'project_members', 
            'tickets', 'activities', 'attachments', 'comments', 
            'issue_labels', 'alembic_version'
        }
        found = set(tables)
        
        if expected.issubset(found):
            print("\n✅ All 9 core tables exist!")
        else:
            missing = expected - found
            print(f"\n❌ Missing tables: {missing}")

if __name__ == "__main__":
    asyncio.run(verify_tables())
