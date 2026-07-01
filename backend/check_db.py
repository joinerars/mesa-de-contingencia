import psycopg2
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")

DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("""
    SELECT table_schema, table_name 
    FROM information_schema.tables 
    WHERE table_schema NOT IN ('information_schema', 'pg_catalog') 
    AND table_name IN ('publicaciones', 'usuarios', 'actividades')
""")
for row in cur.fetchall():
    print(row)
conn.close()
