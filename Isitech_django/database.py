import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    'host': 'localhost',
    'database': 'isitech', 
    'user': 'maxime',  
    'password': 'admin', 
    'port': '5432'
}

def connect_to_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Connection successful!")
        
        cur = conn.cursor()
        
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print(f"PostgreSQL version: {db_version[0]}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")

if __name__ == "__main__":
    connect_to_db()