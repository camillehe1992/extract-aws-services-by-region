import json
import requests


REGIONS = ["cn-north-1", "cn-northwest-1", "eu-central-1"]


def extract_regions(content: dict) -> dict:
    result = []
    for item in content.get("prices"):
        if item["id"].split(":").pop() in REGIONS:
            result.append(item["attributes"])
    return result


def lambda_handler(event, context):
    response = requests.get("https://api.regional-table.region-services.aws.a2z.com")
    content = response.json()
    extracted_content = extract_regions(content)
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": extracted_content,
    }


# Using the special variable
# __name__
if __name__ == "__main__":
    response = lambda_handler({}, {})
    print(json.dumps(response, indent=2))
