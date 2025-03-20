import json
import boto3

def lambda_handler(event, context):
    
    # Retrieve the database 
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('DespatchAdviceTable')

    # Check if event contains the despatch ID, if not return response: 400
    if 'despatchId' not in event.get('pathParameters', {}):
        return {
            "statusCode": 400,
            "body": "Bad Request - The despatch ID is not provided"
        }

    despatch_id = event['pathParameters']['despatchId']

    response = table.get_item(Key={'ID': despatch_id})
    # if item doesn't exist in the response, return response: 404
    if 'Item' not in response:
        return {
            "statusCode": 404,
            "body": "No content - The despatch ID is invalid"
        }

    # Get the OrderReference attribute string from the Item associated with ID
    despatch_advice = response['Item']
    order_reference_details = despatch_advice.get('OrderReference')
    
    #return success: 200 + items
    return {
        "statusCode": 200,
        "Items": order_reference_details
    }