import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import random

# Configuración
OUTPUT_DIR = Path(__file__).parent / "example-data"
SCHEMAS_DIR = Path(__file__).parent / "schemas-validation"

# Datos base para generar ejemplos realistas
NOMBRES = [
    "Juan Pérez", "María García", "Carlos López", "Ana Martínez",
    "Luis Rodríguez", "Carmen Fernández", "José González", "Laura Sánchez",
    "Miguel Torres", "Isabel Ramírez", "Pedro Flores", "Sofía Castro",
    "Diego Morales", "Valentina Ortiz", "Andrés Silva", "Camila Rojas"
]

CORREOS_DOMINIOS = ["utec.edu.pe", "gmail.com", "outlook.com"]

TITULOS_INCIDENTES = [
    "Fuga de agua en baño",
    "Luz fundida en pasillo",
    "Ventana rota en aula",
    "Piso resbaladizo",
    "Puerta atascada",
    "Aire acondicionado no funciona",
    "Proyector dañado",
    "Silla rota",
    "Mesa inestable",
    "Escalera con pasamanos suelto"
]

DESCRIPCIONES_INCIDENTES = [
    "Se requiere atención inmediata",
    "Problema detectado durante inspección de rutina",
    "Reportado por múltiples usuarios",
    "Afecta el uso normal del área",
    "Necesita reparación urgente",
    "Situación de riesgo para estudiantes",
    "Problema recurrente en esta área",
    "Requiere evaluación por especialista"
]

SERVICIOS = ["usuarios", "incidentes", "notificaciones", "analitica", "conexiones"]

MENSAJES_LOG = [
    "Usuario autenticado exitosamente",
    "Error al procesar solicitud",
    "Conexión establecida",
    "Timeout en operación",
    "Datos guardados correctamente",
    "Error de validación",
    "Servicio iniciado",
    "Operación completada"
]


def generar_correo(nombre):
    """Genera un correo electrónico basado en el nombre"""
    nombre_limpio = nombre.lower().replace(" ", ".")
    dominio = random.choice(CORREOS_DOMINIOS)
    return f"{nombre_limpio}@{dominio}"


def generar_telefono():
    """Genera un número de teléfono peruano"""
    return f"+51 9{random.randint(10000000, 99999999)}"


def generar_usuarios(cantidad=10):
    """Genera datos de ejemplo para usuarios"""
    usuarios = []
    roles = ["estudiante", "personal_administrativo", "autoridad"]
    
    for i in range(cantidad):
        nombre = random.choice(NOMBRES)
        usuario = {
            "usuario_id": str(uuid.uuid4()),
            "correo": generar_correo(nombre),
            "contraseña": f"hash_{uuid.uuid4().hex[:16]}",  # Simula un hash
            "nombre": nombre,
            "rol": random.choice(roles)
        }
        usuarios.append(usuario)
    
    return usuarios


def generar_empleados(cantidad=8):
    """Genera datos de ejemplo para empleados"""
    empleados = []
    tipos_area = ["mantenimiento", "electricidad", "limpieza", "seguridad", "ti", "logistica", "otros"]
    estados = ["activo", "inactivo"]
    
    for i in range(cantidad):
        nombre = random.choice(NOMBRES)
        empleado = {
            "empleado_id": str(uuid.uuid4()),
            "nombre": nombre,
            "tipo_area": random.choice(tipos_area),
            "estado": random.choice(estados) if random.random() > 0.2 else "activo",  # 80% activos
            "contacto": {
                "telefono": generar_telefono(),
                "correo": generar_correo(nombre)
            }
        }
        empleados.append(empleado)
    
    return empleados


def generar_incidentes(usuarios, cantidad=15):
    """Genera datos de ejemplo para incidentes"""
    incidentes = []
    tipos = ["limpieza", "TI", "seguridad", "mantenimiento", "otro"]
    niveles_urgencia = ["bajo", "medio", "alto", "critico"]
    estados = ["reportado", "en_progreso", "resuelto"]
    
    for i in range(cantidad):
        creado_en = datetime.now() - timedelta(days=random.randint(0, 30))
        tiene_actualizacion = random.random() > 0.5
        
        incidente = {
            "incidente_id": str(uuid.uuid4()),
            "titulo": random.choice(TITULOS_INCIDENTES),
            "descripcion": random.choice(DESCRIPCIONES_INCIDENTES),
            "piso": random.randint(1, 5),
            "ubicacion": {
                "x": round(random.uniform(-77.0, -76.9), 6),
                "y": round(random.uniform(-12.1, -12.0), 6)
            },
            "tipo": random.choice(tipos),
            "nivel_urgencia": random.choice(niveles_urgencia),
            "evidencias": [
                f"https://storage.example.com/evidencias/{uuid.uuid4()}.jpg"
            ] if random.random() > 0.3 else [],
            "estado": random.choice(estados),
            "usuario_correo": random.choice(usuarios)["correo"],
            "creado_en": creado_en.isoformat()
        }
        
        if tiene_actualizacion:
            incidente["actualizado_en"] = (creado_en + timedelta(hours=random.randint(1, 48))).isoformat()
        
        incidentes.append(incidente)
    
    return incidentes


def generar_registros(cantidad=20):
    """Genera datos de ejemplo para registros (logs)"""
    registros = []
    niveles = ["INFO", "WARNING", "ERROR", "CRITICAL"]
    
    for i in range(cantidad):
        nivel = random.choice(niveles)
        servicio = random.choice(SERVICIOS)
        
        registro = {
            "registro_id": str(uuid.uuid4()),
            "nivel": nivel,
            "mensaje": random.choice(MENSAJES_LOG),
            "servicio": servicio,
            "contexto": {
                "request_id": str(uuid.uuid4()),
                "user_agent": "AWS Lambda",
                "ip": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
            },
            "marca_tiempo": (datetime.now() - timedelta(hours=random.randint(0, 72))).isoformat()
        }
        registros.append(registro)
    
    return registros


def generar_conexiones(usuarios, cantidad=12):
    """Genera datos de ejemplo para conexiones WebSocket"""
    conexiones = []
    
    for i in range(cantidad):
        fecha_conexion = datetime.now() - timedelta(minutes=random.randint(0, 120))
        # TTL en segundos (expira en 2 horas desde la conexión)
        expiracion_ttl = int((fecha_conexion + timedelta(hours=2)).timestamp())
        
        conexion = {
            "conexion_id": str(uuid.uuid4()),
            "usuario_id": random.choice(usuarios)["usuario_id"],
            "fecha_conexion": fecha_conexion.isoformat(),
            "expiracion_ttl": expiracion_ttl
        }
        conexiones.append(conexion)
    
    return conexiones


def validar_con_esquema(datos, nombre_esquema):
    """Valida que los datos cumplan con el esquema definido"""
    try:
        with open(SCHEMAS_DIR / f"{nombre_esquema}.json", "r", encoding="utf-8") as f:
            esquema = json.load(f)
        
        # Verificar propiedades requeridas
        required = esquema.get("required", [])
        for item in datos:
            for campo in required:
                if campo not in item:
                    print(f"⚠️  Advertencia: Falta campo requerido '{campo}' en {nombre_esquema}")
                    return False
        
        print(f"✅ Datos de {nombre_esquema} validados correctamente")
        return True
    except Exception as e:
        print(f"❌ Error al validar {nombre_esquema}: {e}")
        return False


def guardar_json(datos, nombre_archivo):
    """Guarda los datos en un archivo JSON"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    ruta = OUTPUT_DIR / nombre_archivo
    
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
    
    print(f"📝 Generado: {ruta} ({len(datos)} registros)")


def main():
    """Función principal que orquesta la generación de datos"""
    print("=" * 60)
    print("🚀 GENERADOR DE DATOS - HCKT-CLOUD")
    print("=" * 60)
    print()
    
    # Generar usuarios primero (son referenciados por otros)
    print("📊 Generando usuarios...")
    usuarios = generar_usuarios(10)
    validar_con_esquema(usuarios, "usuarios")
    guardar_json(usuarios, "usuarios.json")
    print()
    
    # Generar empleados
    print("📊 Generando empleados...")
    empleados = generar_empleados(8)
    validar_con_esquema(empleados, "empleados")
    guardar_json(empleados, "empleados.json")
    print()
    
    # Generar incidentes (requiere usuarios)
    print("📊 Generando incidentes...")
    incidentes = generar_incidentes(usuarios, 15)
    validar_con_esquema(incidentes, "incidentes")
    guardar_json(incidentes, "incidentes.json")
    print()
    
    # Generar registros
    print("📊 Generando registros (logs)...")
    registros = generar_registros(20)
    validar_con_esquema(registros, "logs")
    guardar_json(registros, "logs.json")
    print()
    
    # Generar conexiones (requiere usuarios)
    print("📊 Generando conexiones...")
    conexiones = generar_conexiones(usuarios, 12)
    validar_con_esquema(conexiones, "conexiones")
    guardar_json(conexiones, "conexiones.json")
    print()
    
    print("=" * 60)
    print("✨ Generación completada exitosamente")
    print(f"📂 Archivos guardados en: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
