import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

# Ya no usamos SCHEMA = "MesaDeContingencia" porque en Postgres usaremos "public" por defecto.

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

