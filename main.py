from os import environ as env
import json
import logging
import requests
import xlsxwriter
import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.DEBUG)

# Environment Variables
XLSX_FILE_S3_BUKCET_NAME = env.get(
    "XLSX_FILE_S3_BUKCET_NAME", "extract-services-by-region-above-mallard"
)
TARGET_REGIONS = env.get("TARGET_REGIONS", "cn-north-1,cn-northwest-1,eu-central-1")
AWS_SERVICES_API_URL = env.get(
    "AWS_SERVICES_API_URL", "https://api.regional-table.region-services.aws.a2z.com"
)

# Constants
REGIONS = TARGET_REGIONS.split(",")
XLSX_HEADERS = ["AWS Service"] + REGIONS
XLSX_FILE_S3_OBJECT_KEY = "aws_services_availability_by_regions.xlsx"
AWS_REGION = env.get("AWS_REGION", "cn-north-1")
PRESIGNED_URL_EXPIRATION_IN_SECOND = 600


def save_to_local_file(obj, path):
    with open(path, encoding="utf-8", mode="w+") as f:
        f.write(json.dumps(obj))


def get_services_details(url: str = AWS_SERVICES_API_URL):
    response = requests.get(url, timeout=10)
    content = response.json()
    logging.info("Get list of AWS services available from API %s", url)
    return content


def extract_regions(content: dict) -> dict:
    result = {}
    for item in content.get("prices"):
        region = item["id"].split(":").pop()
        if region in REGIONS:
            if result.get(region):
                result[region].append(
                    {
                        "service_name": item["attributes"]["aws:serviceName"],
                        "service_url": item["attributes"]["aws:serviceUrl"],
                    }
                )
            else:
                result[region] = [
                    {
                        "service_name": item["attributes"]["aws:serviceName"],
                        "service_url": item["attributes"]["aws:serviceUrl"],
                    }
                ]
    return result


def construct_services_dictionary(content: dict) -> set:
    services_set = set()
    services_dict = {}
    for key, value in content.items():
        services_dict[key] = [item["service_name"] for item in value]
    services_set.update(*services_dict.values())
    return sorted(services_set)


def is_available(service_name: str, content: list) -> str:
    return "Y" if service_name in [item["service_name"] for item in content] else "N"


def generate_xlsx_data(content: dict, services_dictionary: set) -> dict:
    xlsx_data = []
    for service_name in services_dictionary:
        row_data = []
        row_data.append(service_name)
        for region in REGIONS:
            row_data.append(is_available(service_name, content[region]))
        xlsx_data.append(tuple(row_data))
    return xlsx_data


def availability_consistent(availability: list) -> bool:
    return len(set(availability)) == 1


def write_to_xlsx_file(
    xlsx_data: dict, file_name: str = XLSX_FILE_S3_OBJECT_KEY
) -> None:
    workbook = xlsxwriter.Workbook(f"/tmp/{file_name}")
    worksheet = workbook.add_worksheet()
    format = workbook.add_format({"bold": True, "bg_color": "yellow"})
    row_num = 0
    worksheet.write_row(0, 0, XLSX_HEADERS)
    for row_data in xlsx_data:
        row_num += 1
        if availability_consistent(availability=row_data[1:]):
            worksheet.write_row(row_num, 0, row_data)
        else:
            worksheet.write_row(row_num, 0, row_data, format)
    workbook.close()


def upload_to_s3(file_path: str = f"/tmp/{XLSX_FILE_S3_OBJECT_KEY}") -> bool:
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    try:
        params = {
            "Filename": file_path,
            "Bucket": XLSX_FILE_S3_BUKCET_NAME,
            "Key": XLSX_FILE_S3_OBJECT_KEY,
        }
        logging.info("S3 upload params", extra=params)
        s3_client.upload_file(**params)
        logging.info("S3 object is uploaded successfully")
        return True
    except ClientError as err:
        logging.error("Failed to upload to S3", extra=err)
        return False


def create_presigned_url(
    bucket_name: str = XLSX_FILE_S3_BUKCET_NAME,
    object_name: str = XLSX_FILE_S3_OBJECT_KEY,
    expiration: int = PRESIGNED_URL_EXPIRATION_IN_SECOND,
):
    # Generate a presigned URL for the S3 object
    s3_client = boto3.client(
        "s3",
        region_name=AWS_REGION,
        config=boto3.session.Config(signature_version="s3v4"),
    )
    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
    except Exception as e:
        print(e)
        logging.error(e)
        return "Error"
    # The response contains the presigned URL
    return response


def lambda_handler(event, context):
    content = get_services_details()
    extracted_content = extract_regions(content)
    services_dict = construct_services_dictionary(extracted_content)
    xlsx_data = generate_xlsx_data(extracted_content, services_dict)
    write_to_xlsx_file(xlsx_data)
    response = upload_to_s3()
    if response:
        presigned_url = create_presigned_url()

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": presigned_url,
    }


# Using the special variable
# __name__
if __name__ == "__main__":
    response = lambda_handler({}, {})
    logging.debug(response)
