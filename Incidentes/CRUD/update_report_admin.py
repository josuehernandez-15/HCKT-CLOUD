import os
import json
from datetime import datetime, timezone
import boto3
from CRUD.utils import validar_token
from botocore.exceptions import ClientError
import requests  # NUEVO

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_INCIDENTES')
incidentes_table = dynamodb.Table(table_name)

ESTADO_ENUM = ["reportado", "en_progreso", "resuelto"]
ADMIN_ESTADOS_PERMITIDOS = ["en_progreso", "resuelto"]

BREVO_API_KEY = os.environ.get("BREVO_API_KEY")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "no-reply@example.com")


def enviar_correo_cambio_estado(correo_destino, incidente, estado_nuevo):
    """
    Envía un correo al creador de la incidencia cada vez que cambia el estado.
    No rompe la Lambda si falla el envío.
    """
    if not correo_destino:
        print("Incidente sin usuario_correo, no se puede enviar notificación de estado.")
        return

    if not BREVO_API_KEY or not EMAIL_FROM:
        print("Brevo no configurado (falta BREVO_API_KEY o EMAIL_FROM)")
        return

    estado_legible = {
        "reportado": "reportado",
        "en_progreso": "en progreso",
        "resuelto": "resuelto"
    }.get(estado_nuevo, estado_nuevo)

    asunto = "Actualización de tu incidencia - Alerta UTEC"

    html = f"""
        <p>Hola,</p>
        <p>Te informamos que el estado de tu incidencia en <strong>Alerta UTEC</strong> ha cambiado.</p>
        <p><strong>Nuevo estado:</strong> {estado_legible.upper()}</p>
        <p><strong>Detalle de la incidencia:</strong></p>
        <ul>
            <li><strong>Título:</strong> {incidente.get("titulo")}</li>
            <li><strong>Código de seguimiento:</strong> {incidente.get("incidente_id")}</li>
        </ul>
        <p>Gracias por usar la plataforma para reportar incidencias en UTEC. 🏫</p>
        <p><em>Por favor, no respondas a este correo. Ha sido generado automáticamente.</em></p>
    """

    url = "https://api.brevo.com/v3/smtp/email"
    payload = {
        "sender": {"email": EMAIL_FROM},
        "to": [{"email": correo_destino}],
        "subject": asunto,
        "htmlContent": html,
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": BREVO_API_KEY,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        print(
            "Correo de cambio de estado enviado. Status:",
            resp.status_code,
            "Body:",
            resp.text,
        )
    except Exception as e:
        print("Error al enviar correo de cambio de estado:", repr(e))


def lambda_handler(event, context):
    headers = event.get("headers") or {}
    auth_header = headers.get("Authorization") or headers.get("authorization") or ""
    if auth_header.lower().startswith("bearer "):
        auth_header = auth_header.split(" ", 1)[1].strip()
    token = auth_header

    resultado_validacion = validar_token(token)
    
    if not resultado_validacion.get("valido"):
        return {
            "statusCode": 401,
            "body": json.dumps({"message": resultado_validacion.get("error")})
        }
    
    usuario_autenticado = {
        "correo": resultado_validacion.get("correo"),
        "rol": resultado_validacion.get("rol")
    }
    
    if usuario_autenticado["rol"] not in ["personal_administrativo", "autoridad"]:
        return {
            "statusCode": 403,
            "body": json.dumps({"message": "Solo un administrador puede cambiar el estado del incidente"})
        }

    body = json.loads(event.get('body', '{}'))
    
    incidente_id = body.get('incidente_id')
    if not incidente_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Falta 'incidente_id' en el body"})
        }

    if "estado" not in body:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Falta 'estado' en el body"})
        }

    estado_nuevo = body["estado"]

    if estado_nuevo not in ESTADO_ENUM or estado_nuevo not in ADMIN_ESTADOS_PERMITIDOS:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "El estado debe ser 'en_progreso' o 'resuelto' para Admin"})
        }

    try:
        response = incidentes_table.get_item(Key={'incidente_id': incidente_id})
        if 'Item' not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "Incidente no encontrado"})
            }
        
        incidente_actual = response['Item']
    except ClientError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Error al obtener el incidente: {str(e)}"})
        }

    incidente_actual["estado"] = estado_nuevo
    incidente_actual["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    try:
        incidentes_table.put_item(Item=incidente_actual)

        correo_creador = incidente_actual.get("usuario_correo")
        enviar_correo_cambio_estado(
            correo_destino=correo_creador,
            incidente=incidente_actual,
            estado_nuevo=estado_nuevo
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Estado actualizado correctamente",
                "incidente_id": incidente_id,
                "nuevo_estado": estado_nuevo
            })
        }
    except ClientError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Error al actualizar el incidente: {str(e)}"})
        }
