"""
Handler para poblar las tablas DynamoDB con datos de ejemplo
"""

import json
import boto3
import os
from pathlib import Path
from decimal import Decimal
import urllib3

# Cliente DynamoDB
dynamodb = boto3.resource('dynamodb')

# Nombres de las tablas desde variables de entorno
TABLES = {
    'usuarios': os.environ.get('TABLE_USUARIOS'),
    'incidentes': os.environ.get('TABLE_INCIDENTES'),
    'empleados': os.environ.get('TABLE_EMPLEADOS'),
    'logs': os.environ.get('TABLE_LOGS'),
    'conexiones': os.environ.get('TABLE_CONEXIONES')
}

# Directorio de datos de ejemplo
DATA_DIR = Path(__file__).parent / "example-data"

# HTTP client para respuestas de CloudFormation
http = urllib3.PoolManager()


def send_cfn_response(event, context, response_status, response_data):
    """
    Envía respuesta a CloudFormation Custom Resource
    """
    response_body = {
        'Status': response_status,
        'Reason': f'See CloudWatch Log Stream: {context.log_stream_name}',
        'PhysicalResourceId': context.log_stream_name,
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Data': response_data
    }
    
    json_response = json.dumps(response_body)
    
    headers = {
        'content-type': '',
        'content-length': str(len(json_response))
    }
    
    try:
        response = http.request(
            'PUT',
            event['ResponseURL'],
            body=json_response,
            headers=headers
        )
        print(f"CloudFormation response status: {response.status}")
    except Exception as e:
        print(f"Error sending response to CloudFormation: {e}")


def decimal_converter(obj):
    """Convierte float a Decimal para DynamoDB"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: decimal_converter(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_converter(item) for item in obj]
    return obj


def cargar_datos_json(archivo):
    """Carga datos desde un archivo JSON"""
    ruta = DATA_DIR / archivo
    print(f"Cargando datos desde: {ruta}")
    with open(ruta, 'r', encoding='utf-8') as f:
        datos = json.load(f)
        # Convertir floats a Decimal para DynamoDB
        return [decimal_converter(item) for item in datos]


def poblar_tabla(tabla_nombre, datos):
    """Puebla una tabla DynamoDB con los datos proporcionados"""
    tabla = dynamodb.Table(tabla_nombre)
    print(f"Poblando tabla {tabla_nombre} con {len(datos)} registros...")
    
    with tabla.batch_writer() as batch:
        for item in datos:
            batch.put_item(Item=item)
    
    print(f"✅ Tabla {tabla_nombre} poblada con {len(datos)} registros")
    return len(datos)


def poblar_datos_custom_resource(event, context):
    """
    Custom Resource para poblar datos automáticamente al crear el stack
    """
    print(f"Evento recibido: {json.dumps(event)}")
    
    try:
        request_type = event['RequestType']
        
        # Solo poblar en Create, ignorar en Update y Delete
        if request_type == 'Create':
            resultados = {}
            
            # Esperar un momento para que las tablas estén completamente creadas
            import time
            time.sleep(5)
            
            # Poblar cada tabla
            for nombre, tabla in TABLES.items():
                if not tabla:
                    print(f"⚠️  Variable de entorno TABLE_{nombre.upper()} no definida")
                    resultados[nombre] = {
                        'status': 'skipped',
                        'mensaje': f'Variable de entorno no definida'
                    }
                    continue
                
                try:
                    archivo = f"{nombre}.json"
                    datos = cargar_datos_json(archivo)
                    cantidad = poblar_tabla(tabla, datos)
                    
                    resultados[nombre] = {
                        'status': 'success',
                        'tabla': tabla,
                        'registros_insertados': cantidad
                    }
                except Exception as e:
                    print(f"❌ Error poblando {nombre}: {str(e)}")
                    resultados[nombre] = {
                        'status': 'error',
                        'tabla': tabla,
                        'mensaje': str(e)
                    }
            
            # Enviar respuesta de éxito
            send_cfn_response(event, context, 'SUCCESS', {
                'Message': 'Datos poblados exitosamente',
                'Resultados': json.dumps(resultados)
            })
        
        elif request_type in ['Update', 'Delete']:
            # No hacer nada en Update o Delete
            print(f"RequestType '{request_type}' - No se requiere acción")
            send_cfn_response(event, context, 'SUCCESS', {
                'Message': f'{request_type} - Sin acción requerida'
            })
    
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")
        import traceback
        traceback.print_exc()
        send_cfn_response(event, context, 'FAILED', {
            'Message': str(e)
        })


def poblar_datos(event, context):
    """
    Función Lambda para poblar todas las tablas con datos de ejemplo (Manual via HTTP)
    """
    try:
        resultados = {}
        
        # Poblar cada tabla
        for nombre, tabla in TABLES.items():
            if not tabla:
                resultados[nombre] = {
                    'status': 'error',
                    'mensaje': f'Variable de entorno TABLE_{nombre.upper()} no definida'
                }
                continue
            
            try:
                archivo = f"{nombre}.json"
                datos = cargar_datos_json(archivo)
                cantidad = poblar_tabla(tabla, datos)
                
                resultados[nombre] = {
                    'status': 'success',
                    'tabla': tabla,
                    'registros_insertados': cantidad
                }
            except Exception as e:
                resultados[nombre] = {
                    'status': 'error',
                    'tabla': tabla,
                    'mensaje': str(e)
                }
        
        # Determinar el código de respuesta
        todos_exitosos = all(r['status'] == 'success' for r in resultados.values())
        status_code = 200 if todos_exitosos else 207  # 207 = Multi-Status
        
        return {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'mensaje': 'Población de datos completada',
                'resultados': resultados
            }, ensure_ascii=False, indent=2)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Error al poblar datos',
                'detalle': str(e)
            }, ensure_ascii=False)
        }
