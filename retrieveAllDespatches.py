import json
import boto3

def lambda_handler(event, context):
    client = boto3.client('dynamodb')

    # Scan the table to retrieve all items
    response = client.scan(TableName='DespatchAdviceTable')

    # Extract only the 'ID' field from all items
    ids = [item['ID']['N'] for item in response.get('Items', [])]
    if not ids:
        return {
            "statusCode": 204,
            "body": {"message": "No despatch advice found"}
        }

    return {
        'statusCode': 200,
        'despatchAdvices': {
            "despatchAdvicesIDs": [f"ID: {id}" for id in ids]
        }
    }