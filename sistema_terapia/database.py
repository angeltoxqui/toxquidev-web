import mysql.connector
from mysql.connector import pooling
import os  # <-- 1. Importamos OS para leer variables del sistema
from dotenv import load_dotenv # <-- 2. Importamos dotenv

# 3. Cargar variables del archivo .env (solo funcionará en tu PC local)
load_dotenv()

# 4. Configuración usando os.getenv
# Si no encuentra la variable, puedes poner un valor por defecto o dejarlo que falle
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "autocommit": True,
    "auth_plugin": 'mysql_native_password'
}

# Inicializar el pool de conexiones
try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="terapia_pool",
        pool_size=5,
        pool_reset_session=True,
        **db_config
    )
except mysql.connector.Error as err:
    print(f"❌ Error creando pool de conexiones: {err}")
    connection_pool = None

def get_db_connection():
    try:
        if connection_pool:
            return connection_pool.get_connection()
        else:
            return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"❌ Error conectando a Hostinger: {err}")
        return None