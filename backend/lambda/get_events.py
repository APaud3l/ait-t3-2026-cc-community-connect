import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Events")


def lambda_handler(event, context):
    try:
        result = table.scan()
        events = result["Items"]

        for item in events:
            item["id"] = int(item["id"])

        events.sort(key=lambda e: (e["event_date"], e["id"]))

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(events)
        }

    except ClientError as error:
        print(error)

        return {
            "statusCode": 503,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Database unavailable"})
        }