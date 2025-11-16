"""
Handler placeholder para el microservicio de Incidentes
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
            'mensaje': 'Microservicio de Incidentes - En desarrollo',
            'servicio': 'alerta-utec-incidentes'
        })
    }
