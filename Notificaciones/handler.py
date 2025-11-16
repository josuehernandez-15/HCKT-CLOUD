"""
Handler para el microservicio de Notificaciones (WebSocket)
"""

import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
tabla_conexiones = dynamodb.Table(os.environ.get('TABLE_CONEXIONES'))


def connect(event, context):
    """
    Maneja nuevas conexiones WebSocket
    """
    connection_id = event['requestContext']['connectionId']
    
    # TODO: Extraer usuario_id del token de autenticación
    # Por ahora usamos un placeholder
    
    try:
        # Guardar conexión en DynamoDB
        tabla_conexiones.put_item(
            Item={
                'conexion_id': connection_id,
                'usuario_id': 'placeholder',  # TODO: obtener del token
                'fecha_conexion': context.get_remaining_time_in_millis()
            }
        )
        
        return {'statusCode': 200}
    except Exception as e:
        return {'statusCode': 500, 'body': str(e)}


def disconnect(event, context):
    """
    Maneja desconexiones WebSocket
    """
    connection_id = event['requestContext']['connectionId']
    
    try:
        # Eliminar conexión de DynamoDB
        tabla_conexiones.delete_item(
            Key={'conexion_id': connection_id}
        )
        
        return {'statusCode': 200}
    except Exception as e:
        return {'statusCode': 500, 'body': str(e)}


def placeholder(event, context):
    """
    Función placeholder temporal
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'mensaje': 'Microservicio de Notificaciones - En desarrollo',
            'servicio': 'alerta-utec-notificaciones'
        })
    }
