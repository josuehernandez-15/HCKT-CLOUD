"""
Handler principal para el microservicio de Incidentes
"""

import os
import json
import uuid
import base64
import boto3
from datetime import datetime
from decimal import Decimal
from botocore.exceptions import ClientError
from utils import validar_token

# Clientes AWS
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Variables de entorno
TABLE_INCIDENTES = os.environ.get('TABLE_INCIDENTES')
INCIDENTES_BUCKET = os.environ.get('INCIDENTES_BUCKET')

# Tablas DynamoDB
incidentes_table = dynamodb.Table(TABLE_INCIDENTES)

# Enums de validación
TIPO_ENUM = ["limpieza", "TI", "seguridad", "mantenimiento", "otro"]
NIVEL_URGENCIA_ENUM = ["bajo", "medio", "alto", "critico"]
ESTADO_ENUM = ["reportado", "en_progreso", "resuelto"]
PISO_RANGO = range(-2, 12)


def _response(status_code, body):
    """Helper para generar respuestas HTTP consistentes"""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body, ensure_ascii=False, default=str)
    }


def _subir_evidencia_s3(evidencia_data):
    """Sube una evidencia a S3 y retorna la URL"""
    try:
        key = evidencia_data.get("key")
        file_b64 = evidencia_data.get("file_base64")
        content_type = evidencia_data.get("content_type", "image/jpeg")
        
        if not key or not file_b64:
            raise ValueError("Faltan 'key' o 'file_base64' en evidencia")
        
        file_bytes = base64.b64decode(file_b64)
        
        s3.put_object(
            Bucket=INCIDENTES_BUCKET,
            Key=key,
            Body=file_bytes,
            ContentType=content_type
        )
        
        return f"s3://{INCIDENTES_BUCKET}/{key}"
    
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code == "AccessDenied":
            raise ValueError("Acceso denegado al bucket de evidencias")
        if code == "NoSuchBucket":
            raise ValueError(f"El bucket {INCIDENTES_BUCKET} no existe")
        raise ValueError(f"Error al subir evidencia a S3: {str(e)}")


def crear_incidente(event, context):
    """Crea un nuevo incidente"""
    try:
        # Validar token
        token = event.get("headers", {}).get("authorization", "").replace("Bearer ", "")
        resultado_validacion = validar_token(token)
        
        if not resultado_validacion.get("valido"):
            return _response(401, {"error": resultado_validacion.get("error")})
        
        usuario = resultado_validacion
        
        # Solo usuarios y admins pueden crear incidentes
        if usuario["role"] not in ["user", "admin", "estudiante", "personal_administrativo", "autoridad"]:
            return _response(403, {"error": "No tienes permisos para crear incidentes"})
        
        # Parsear body
        body = json.loads(event.get('body', '{}'))
        
        # Validar campos obligatorios
        required_fields = ["titulo", "descripcion", "piso", "ubicacion", "tipo", "nivel_urgencia"]
        for field in required_fields:
            if field not in body:
                return _response(400, {"error": f"Falta el campo obligatorio: {field}"})
        
        # Validar enums
        if body["tipo"] not in TIPO_ENUM:
            return _response(400, {"error": f"Tipo inválido. Debe ser uno de: {', '.join(TIPO_ENUM)}"})
        
        if body["nivel_urgencia"] not in NIVEL_URGENCIA_ENUM:
            return _response(400, {"error": f"Nivel de urgencia inválido. Debe ser uno de: {', '.join(NIVEL_URGENCIA_ENUM)}"})
        
        if body["piso"] not in PISO_RANGO:
            return _response(400, {"error": "El piso debe estar entre -2 y 11"})
        
        # Procesar evidencias si existen
        evidencias_urls = []
        if 'evidencias' in body and isinstance(body['evidencias'], list):
            for evidencia in body['evidencias']:
                try:
                    url = _subir_evidencia_s3(evidencia)
                    evidencias_urls.append(url)
                except ValueError as e:
                    return _response(400, {"error": str(e)})
        
        # Crear incidente
        incidente_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        incidente = {
            "incidente_id": incidente_id,
            "titulo": body["titulo"],
            "descripcion": body["descripcion"],
            "piso": body["piso"],
            "ubicacion": body["ubicacion"],
            "tipo": body["tipo"],
            "nivel_urgencia": body["nivel_urgencia"],
            "evidencias": evidencias_urls,
            "estado": "reportado",
            "usuario_correo": usuario["correo"],
            "creado_en": timestamp,
            "actualizado_en": timestamp
        }
        
        incidentes_table.put_item(Item=incidente)
        
        return _response(201, {
            "mensaje": "Incidente creado correctamente",
            "incidente_id": incidente_id
        })
    
    except Exception as e:
        print(f"Error al crear incidente: {str(e)}")
        return _response(500, {"error": "Error interno al crear el incidente"})


def actualizar_incidente_usuario(event, context):
    """Actualiza un incidente (solo el usuario que lo creó)"""
    # ...existing code from update_report_users.py adapted...
    return _response(200, {"mensaje": "Funcionalidad en desarrollo"})


def actualizar_incidente_admin(event, context):
    """Actualiza el estado de un incidente (solo admin)"""
    # ...existing code from update_report_admin.py adapted...
    return _response(200, {"mensaje": "Funcionalidad en desarrollo"})


def buscar_incidente(event, context):
    """Busca un incidente por ID"""
    # ...existing code from search_report.py adapted...
    return _response(200, {"mensaje": "Funcionalidad en desarrollo"})


def listar_incidentes(event, context):
    """Lista incidentes con paginación"""
    # ...existing code from list_report.py adapted...
    return _response(200, {"mensaje": "Funcionalidad en desarrollo"})
