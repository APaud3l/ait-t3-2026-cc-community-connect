import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Events")


def response(status, data):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data)
    }


def lambda_handler(event, context):
    try:
        event_id = int(event["pathParameters"]["event_id"])

        if event_id < 1:
            return response(400, {"error": "Invalid event ID"})

    except (KeyError, TypeError, ValueError):
        return response(400, {"error": "Invalid event ID"})

    try:
        result = table.get_item(Key={"id": event_id})
        item = result.get("Item")

        if item is None:
            return response(404, {"error": "Event not found"})

        item["id"] = int(item["id"])

        return response(200, item)

    except ClientError as error:
        print(error)
        return response(503, {"error": "Database unavailable"})