import boto3
import os

# Cargar variables de entorno si existen
region = os.getenv("AWS_REGION", "ap-southeast-2")
endpoint_url = os.getenv("DYNAMODB_ENDPOINT")  # será None en producción

# Configurar recursos y clientes según entorno
if endpoint_url:
    # LOCAL
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=region,
        endpoint_url=endpoint_url,
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )

    dynamodbClient = boto3.client(
        'dynamodb',
        region_name=region,
        endpoint_url=endpoint_url,
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )
else:
    # PRODUCCIÓN EN AWS
    dynamodb = boto3.resource('dynamodb', region_name=region)
    dynamodbClient = boto3.client('dynamodb', region_name=region)
