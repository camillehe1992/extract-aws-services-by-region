import json
import requests
import xlsxwriter

# Constants
REGIONS = ["cn-north-1", "cn-northwest-1", "eu-central-1"]
SERVICES_API_URL = "https://api.regional-table.region-services.aws.a2z.com"
XLSX_HEADERS = ["AWS Service"] + REGIONS


def save_to_local_file(obj, path):
    with open(path, encoding="utf-8", mode="w+") as f:
        f.write(json.dumps(obj))


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
    xlsx_data: dict, file_name: str = "aws_services_availibility_by_regions.xlsx"
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


def lambda_handler(event, context):
    response = requests.get(SERVICES_API_URL, timeout=10)
    content = response.json()
    extracted_content = extract_regions(content)
    services_dict = construct_services_dictionary(extracted_content)
    xlsx_data = generate_xlsx_data(extracted_content, services_dict)
    write_to_xlsx_file(xlsx_data)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": services_dict,
    }


# Using the special variable
# __name__
if __name__ == "__main__":
    response = lambda_handler({}, {})
    save_to_local_file(response, "response.json")
