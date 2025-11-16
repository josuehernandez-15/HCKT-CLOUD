"""
Handler para poblar las tablas DynamoDB con datos de ejemplo
"""

import json
import boto3
import os
from pathlib import Path
from decimal import Decimal

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
    with open(ruta, 'r', encoding='utf-8') as f:
        datos = json.load(f)
        # Convertir floats a Decimal para DynamoDB
        return [decimal_converter(item) for item in datos]


def poblar_tabla(tabla_nombre, datos):
    """Puebla una tabla DynamoDB con los datos proporcionados"""
    tabla = dynamodb.Table(tabla_nombre)
    
    with tabla.batch_writer() as batch:
        for item in datos:
            batch.put_item(Item=item)
    
    return len(datos)


def poblar_datos(event, context):
    """
    Función Lambda principal para poblar todas las tablas con datos de ejemplo
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
