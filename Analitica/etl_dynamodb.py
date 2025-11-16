from airflow import DAG
from airflow.decorators import task
from airflow.hooks.base import BaseHook
from datetime import datetime
import json
from decimal import Decimal
import boto3
import time

# ====== CONFIGURACIÓN BÁSICA ======
DYNAMO_TABLES = ["tabla_1", "tabla_2", "tabla_3"]  # <-- pon aquí tus tablas reales
S3_BUCKET_EXPORT = "mi-bucket-destino"             # <-- bucket donde guardarás los JSON
S3_PREFIX_BASE = "dynamo_export"                   # prefijo base en S3
GLUE_CRAWLER_NAME = "crawler_dynamo"               # <-- tu crawler de Glue
GLUE_DATABASE = "mi_db"                            # <-- tu Glue/Athena DB
ATHENA_OUTPUT = "s3://mi-bucket-athena-results/dynamo_export/"  # <-- output de Athena
AWS_REGION = "us-east-1"                           # <-- ajusta tu región

# ====== DEFINICIÓN DEL DAG ======
dag = DAG(
    "etl_dynamodb_a_s3_glue_athena",
    description="ETL de 3 tablas DynamoDB a S3 (JSON) -> Glue -> Athena",
    schedule_interval="@once",   # o @daily si quieres que corra todos los días
    start_date=datetime(2024, 1, 1),
    catchup=False,
)

# ====== HELPERS PARA CREDENCIALES Y JSON ======

def get_aws_credentials():
    conn = BaseHook.get_connection("aws_credentials")
    aws_credentials = {
        "access_key": conn.login,
        "secret_access_key": conn.password,
        "session_token": conn.extra_dejson.get("aws_session_token"),
        "region_name": conn.extra_dejson.get("region_name", AWS_REGION),
    }
    return aws_credentials

def decimal_default(obj):
    """Convertir Decimal de DynamoDB a float para JSON."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def upload_json_lines(s3_client, bucket, key_prefix, table_name, part, items):
    # JSON Lines: un objeto JSON por línea
    lines = [json.dumps(item, default=decimal_default) for item in items]
    body = "\n".join(lines)

    key = f"{key_prefix}part-{part:04d}.json"
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=body.encode("utf-8"),
        ContentType="application/json",
    )
    print(f"Subido {len(items)} registros de {table_name} a s3://{bucket}/{key}")

# ====== TASK 1: Exportar las 3 tablas DynamoDB a S3 en JSON ======

@task(dag=dag)
def export_dynamodb_to_s3(execution_date: str = "{{ ds }}"):
    """
    Hace scan a cada tabla de DynamoDB y la sube a S3 como JSON Lines:
    s3://BUCKET/dynamo_export/<tabla>/fecha=YYYY-MM-DD/part-0001.json
    """
    aws_credentials = get_aws_credentials()

    session = boto3.Session(
        aws_access_key_id=aws_credentials["access_key"],
        aws_secret_access_key=aws_credentials["secret_access_key"],
        aws_session_token=aws_credentials["session_token"],
        region_name=aws_credentials["region_name"],
    )

    dynamodb = session.resource("dynamodb")
    s3 = session.client("s3")

    for table_name in DYNAMO_TABLES:
        print(f"Exportando tabla DynamoDB: {table_name}")
        table = dynamodb.Table(table_name)

        date_str = execution_date  # p.ej. 2024-01-01
        key_prefix = f"{S3_PREFIX_BASE}/{table_name}/fecha={date_str}/"

        items = []
        last_evaluated_key = None
        part = 1

        while True:
            scan_kwargs = {}
            if last_evaluated_key:
                scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

            response = table.scan(**scan_kwargs)
            batch_items = response.get("Items", [])

            if not batch_items:
                break

            items.extend(batch_items)

            # Cada 10k registros subimos un archivo para no petar memoria
            if len(items) >= 10000:
                upload_json_lines(s3, S3_BUCKET_EXPORT, key_prefix, table_name, part, items)
                part += 1
                items = []

            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break

        # Subir lo que falte
        if items:
            upload_json_lines(s3, S3_BUCKET_EXPORT, key_prefix, table_name, part, items)

    print("Exportación de todas las tablas DynamoDB completada.")

# ====== TASK 2: Ejecutar Glue Crawler ======

@task(dag=dag)
def run_glue_crawler():
    """
    Lanza el Glue Crawler y espera a que termine.
    """
    aws_credentials = get_aws_credentials()

    session = boto3.Session(
        aws_access_key_id=aws_credentials["access_key"],
        aws_secret_access_key=aws_credentials["secret_access_key"],
        aws_session_token=aws_credentials["session_token"],
        region_name=aws_credentials["region_name"],
    )

    glue = session.client("glue")

    print(f"Iniciando Glue Crawler: {GLUE_CRAWLER_NAME}")
    glue.start_crawler(Name=GLUE_CRAWLER_NAME)

    # Esperar a que el crawler termine (polling simple)
    while True:
        response = glue.get_crawler(Name=GLUE_CRAWLER_NAME)
        state = response["Crawler"]["State"]
        print(f"Estado del crawler: {state}")
        if state == "READY":
            break
        time.sleep(30)

    print("Glue Crawler finalizado.")

# ====== TASK 3: Ejecutar query de validación en Athena ======

@task(dag=dag)
def run_athena_validation(execution_date: str = "{{ ds }}"):
    """
    Ejecuta una query de ejemplo en Athena para validar que se vean las 3 tablas.
    """
    aws_credentials = get_aws_credentials()

    session = boto3.Session(
        aws_access_key_id=aws_credentials["access_key"],
        aws_secret_access_key=aws_credentials["secret_access_key"],
        aws_session_token=aws_credentials["session_token"],
        region_name=aws_credentials["region_name"],
    )

    athena = session.client("athena")

    query = f"""
        SELECT 'tabla_1' AS tabla, count(*) AS registros
        FROM {GLUE_DATABASE}.tabla_1
        WHERE fecha = date '{execution_date}'
        UNION ALL
        SELECT 'tabla_2', count(*)
        FROM {GLUE_DATABASE}.tabla_2
        WHERE fecha = date '{execution_date}'
        UNION ALL
        SELECT 'tabla_3', count(*)
        FROM {GLUE_DATABASE}.tabla_3
        WHERE fecha = date '{execution_date}';
    """

    print("Ejecutando query de validación en Athena:")
    print(query)

    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": GLUE_DATABASE},
        ResultConfiguration={"OutputLocation": ATHENA_OUTPUT},
    )

    query_execution_id = response["QueryExecutionId"]
    print(f"QueryExecutionId: {query_execution_id}")

    # (Opcional) Esperar a que termine y logear estado
    while True:
        res = athena.get_query_execution(QueryExecutionId=query_execution_id)
        state = res["QueryExecution"]["Status"]["State"]
        print(f"Estado de la query Athena: {state}")
        if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(10)

    if state != "SUCCEEDED":
        raise Exception(f"La query de Athena terminó en estado: {state}")

    print("Query de Athena finalizada correctamente.")

# ====== DEPENDENCIAS ======
export_task = export_dynamodb_to_s3()
crawler_task = run_glue_crawler()
athena_task = run_athena_validation()

export_task >> crawler_task >> athena_task