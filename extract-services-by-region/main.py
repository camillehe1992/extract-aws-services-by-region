import requests


def lambda_handler(event, context):
    response = requests.get("https://api.regional-table.region-services.aws.a2z.com")
    content = response.json()
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": content,
    }
