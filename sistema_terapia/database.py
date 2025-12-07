import mysql.connector
from mysql.connector import pooling

# Crear un pool de conexiones para mejor manejo
db_config = {
    "host": "srv1709.hstgr.io",
    "user": "u393944978_admin",
    "password": "ToxquiDev2025*",
    "database": "u393944978_terapia",
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