import sqlite3
import os

DB_NAME = "sales_manager.db"

def inspect_db():
    if not os.path.exists(DB_NAME):
        print(f"Database {DB_NAME} not found!")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\n=== Database Inspection: {DB_NAME} ===")
    print(f"Tables found: {[t[0] for t in tables]}")
    print("=" * 40)

    for table_name in tables:
        table = table_name[0]
        if table == "alembic_version": continue
        
        print(f"\n[Table: {table}]")
        try:
            # Get columns
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Get Rows
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            if not rows:
                print("(Empty)")
            else:
                # Simple formatted printing
                # Calculate max width for each column
                col_widths = [len(c) for c in columns]
                for row in rows:
                    for i, val in enumerate(row):
                        col_widths[i] = max(col_widths[i], len(str(val)))
                
                # Print Header
                header = " | ".join(f"{col:<{col_widths[i]}}" for i, col in enumerate(columns))
                print(header)
                print("-" * len(header))
                
                # Print Rows
                for row in rows:
                    print(" | ".join(f"{str(val):<{col_widths[i]}}" for i, val in enumerate(row)))

        except Exception as e:
            print(f"Error reading {table}: {e}")
            
    conn.close()

if __name__ == "__main__":
    inspect_db()
