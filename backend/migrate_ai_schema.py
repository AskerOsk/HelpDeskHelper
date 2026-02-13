"""
Migration script to add AI-related columns to existing database
"""
import psycopg2
import sys

def migrate_database():
    """Add AI columns to existing schema"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            user='postgres',
            host='127.0.0.1',
            database='sulpak_helpdesk',
            password='postgres',
            port=5432
        )
        conn.autocommit = True
        cursor = conn.cursor()

        print("Starting migration...")

        # Add columns to tickets table
        try:
            cursor.execute("""
                ALTER TABLE tickets
                ADD COLUMN IF NOT EXISTS ai_summary TEXT,
                ADD COLUMN IF NOT EXISTS escalated_at TIMESTAMP;
            """)
            print("[OK] Added ai_summary and escalated_at to tickets table")
        except Exception as e:
            print(f"[WARN] tickets table: {e}")

        # Add column to messages table
        try:
            cursor.execute("""
                ALTER TABLE messages
                ADD COLUMN IF NOT EXISTS ai_confidence FLOAT;
            """)
            print("[OK] Added ai_confidence to messages table")
        except Exception as e:
            print(f"[WARN] messages table: {e}")

        # Update managers table - add email, make telegram_id nullable
        try:
            cursor.execute("""
                ALTER TABLE managers
                ADD COLUMN IF NOT EXISTS email VARCHAR(255);
            """)
            print("[OK] Added email to managers table")
        except Exception as e:
            print(f"[WARN] managers table: {e}")

        try:
            cursor.execute("""
                ALTER TABLE managers
                ALTER COLUMN telegram_id DROP NOT NULL;
            """)
            print("[OK] Made telegram_id nullable in managers table")
        except Exception as e:
            print(f"[WARN] telegram_id nullable: {e}")

        cursor.close()
        conn.close()

        print("\n[SUCCESS] Migration completed!")
        print("You can now run: python run_all.py")

    except psycopg2.OperationalError as e:
        print(f"[ERROR] Could not connect to database: {e}")
        print("\nMake sure PostgreSQL is running on port 5432")
        print("And database 'sulpak_helpdesk' exists (run create_db.py first)")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    migrate_database()
