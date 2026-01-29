import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def verify_cascade():
    # Connect to database
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    
    try:
        # Query to check the foreign key constraint definition
        query = """
        SELECT 
            tc.constraint_name, 
            tc.table_name, 
            kcu.column_name,
            rc.delete_rule,
            rc.update_rule
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.referential_constraints rc
            ON tc.constraint_name = rc.constraint_name
        WHERE tc.table_name = 'project_invitations'
            AND tc.constraint_type = 'FOREIGN KEY'
            AND kcu.column_name = 'project_id';
        """
        
        result = await conn.fetch(query)
        
        print("\n=== Foreign Key Constraint Details ===")
        for row in result:
            print(f"Constraint Name: {row['constraint_name']}")
            print(f"Table: {row['table_name']}")
            print(f"Column: {row['column_name']}")
            print(f"Delete Rule: {row['delete_rule']}")
            print(f"Update Rule: {row['update_rule']}")
            print()
            
            if row['delete_rule'] == 'CASCADE':
                print("✅ CASCADE delete is properly configured!")
            else:
                print("❌ CASCADE delete is NOT configured!")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(verify_cascade())
