"""
Handler placeholder para el microservicio de Usuarios
"""

import json


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
            'mensaje': 'Microservicio de Usuarios - En desarrollo',
            'servicio': 'alerta-utec-usuarios'
        })
    }
