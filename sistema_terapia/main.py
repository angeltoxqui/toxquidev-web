from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import get_db_connection
import mysql.connector

app = FastAPI()

# --- 1. CONFIGURACIÓN DE SEGURIDAD (CORS) ---
# Permite que el Frontend (puerto 5500) hable con el Backend (puerto 8000)
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "*"  # En producción, cambia esto por tu dominio real (app.toxquidev.com)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. MODELOS DE DATOS (ESQUEMAS) ---

class UsuarioCrear(BaseModel):
    nombre: str
    email: str
    password: str
    rol: str = "profesional"

class LoginUsuario(BaseModel):
    email: str
    password: str

class PacienteCrear(BaseModel):
    nombre: str
    tipo: str  # "particular" o "cud"

# --- 3. RUTAS (ENDPOINTS) ---

@app.get("/")
def read_root():
    return {"mensaje": "API del Sistema Terapéutico funcionando 🚀"}

@app.get("/probar-conexion")
def test_db():
    conn = get_db_connection()
    if conn and conn.is_connected():
        conn.close()
        return {"estado": "✅ ÉXITO", "detalle": "Conectado a la Base de Datos de Hostinger"}
    else:
        return {"estado": "❌ ERROR", "detalle": "No se pudo conectar"}

# --- GESTIÓN DE USUARIOS ---

@app.post("/usuarios/")
def crear_usuario(usuario: UsuarioCrear):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Sin conexión a DB")

    try:
        cursor = conn.cursor()
        query = "INSERT INTO usuarios (nombre, email, password_hash, rol) VALUES (%s, %s, %s, %s)"
        valores = (usuario.nombre, usuario.email, usuario.password, usuario.rol)
        cursor.execute(query, valores)
        conn.commit()
        return {"mensaje": f"✅ Usuario {usuario.nombre} creado exitosamente"}
    except mysql.connector.Error as err:
        return {"error": f"❌ Error de base de datos: {err}"}
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

@app.post("/login")
def login(usuario: LoginUsuario):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Sin conexión a DB")
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, nombre, rol, password_hash FROM usuarios WHERE email = %s"
        cursor.execute(query, (usuario.email,))
        user_db = cursor.fetchone()
        
        if user_db and user_db["password_hash"] == usuario.password:
            return {
                "mensaje": "Login exitoso",
                "usuario": {
                    "id": user_db["id"],
                    "nombre": user_db["nombre"],
                    "rol": user_db["rol"]
                }
            }
        
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error técnico: {err}")
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

# --- GESTIÓN DE PACIENTES ---

@app.post("/pacientes/")
def crear_paciente(paciente: PacienteCrear):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Sin conexión DB")
    
    try:
        cursor = conn.cursor()
        query = "INSERT INTO pacientes (nombre, tipo) VALUES (%s, %s)"
        cursor.execute(query, (paciente.nombre, paciente.tipo))
        conn.commit()
        return {"mensaje": f"✅ Paciente {paciente.nombre} registrado"}
    except mysql.connector.Error as err:
        return {"error": str(err)}
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

@app.get("/pacientes/")
def listar_pacientes():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Sin conexión DB")
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Traemos solo los activos y ordenados por el más reciente
        cursor.execute("SELECT * FROM pacientes WHERE activo = TRUE ORDER BY id DESC")
        pacientes = cursor.fetchall()
        return pacientes
    except mysql.connector.Error as err:
        return {"error": str(err)}
    finally:
        if conn.is_connected(): cursor.close(); conn.close()