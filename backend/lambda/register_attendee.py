import json
import re
import uuid
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
events = dynamodb.Table("Events")
registrations = dynamodb.Table("Registrations")


def response(status, data):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data)
    }


def lambda_handler(event, context):
    try:
        data = json.loads(event.get("body") or "{}")
    except (ValueError, TypeError):
        return response(400, {"error": "Invalid JSON"})

    if not isinstance(data, dict):
        return response(400, {"error": "Valid JSON is required"})

    event_id = data.get("event_id")
    name = data.get("name")
    email = data.get("email")

    if type(event_id) is not int or event_id < 1:
        return response(400, {"error": "Invalid event ID"})

    if not isinstance(name, str) or not isinstance(email, str):
        return response(400, {"error": "Name and email are required"})

    name = name.strip()
    email = email.strip()

    if not name or len(name) > 100:
        return response(400, {"error": "Invalid name"})

    if len(email) > 255 or not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", email
    ):
        return response(400, {"error": "Invalid email address"})

    try:
        result = events.get_item(Key={"id": event_id})

        if "Item" not in result:
            return response(404, {"error": "Event not found"})

        registration_id = str(uuid.uuid4())

        registrations.put_item(Item={
            "id": registration_id,
            "event_id": event_id,
            "name": name,
            "email": email
        })

        return response(201, {
            "id": registration_id,
            "message": "Registration successful!"
        })

    except ClientError as error:
        print(error)
        return response(503, {"error": "Database unavailable"})