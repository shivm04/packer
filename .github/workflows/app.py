import json
import boto3
import os
from datetime import datetime

# ------------------------------------------------
# CONFIG
# ------------------------------------------------
REGION = os.environ.get("AWS_REGION", "us-east-1")

MODEL_ID = os.environ.get(
    "MODEL_ID",
    "anthropic.claude-3-haiku-20240307-v1:0"
)

# ------------------------------------------------
# AWS CLIENTS
# ------------------------------------------------
bedrock = boto3.client("bedrock-runtime", region_name=REGION)
ec2 = boto3.client("ec2", region_name=REGION)
s3 = boto3.client("s3")
rds = boto3.client("rds", region_name=REGION)
lambda_client = boto3.client("lambda", region_name=REGION)
iam = boto3.client("iam")
cloudwatch = boto3.client("cloudwatch", region_name=REGION)

# ------------------------------------------------
# AWS ACCOUNT INVENTORY
# ------------------------------------------------

def get_ec2_data():
    instances = []

    paginator = ec2.get_paginator("describe_instances")

    for page in paginator.paginate():
        for res in page["Reservations"]:
            for inst in res["Instances"]:
                instances.append({
                    "InstanceId": inst.get("InstanceId"),
                    "Type": inst.get("InstanceType"),
                    "State": inst.get("State", {}).get("Name"),
                    "PrivateIP": inst.get("PrivateIpAddress", "N/A")
                })

    return instances


def get_s3_data():
    response = s3.list_buckets()

    return [
        {
            "Name": b["Name"],
            "Created": str(b["CreationDate"])
        }
        for b in response["Buckets"]
    ]


def get_rds_data():
    dbs = rds.describe_db_instances()

    return [
        {
            "DBIdentifier": db["DBInstanceIdentifier"],
            "Engine": db["Engine"],
            "Status": db["DBInstanceStatus"]
        }
        for db in dbs["DBInstances"]
    ]


def get_lambda_data():
    functions = []

    paginator = lambda_client.get_paginator("list_functions")

    for page in paginator.paginate():
        for fn in page["Functions"]:
            functions.append({
                "FunctionName": fn["FunctionName"],
                "Runtime": fn["Runtime"],
                "LastModified": fn["LastModified"]
            })

    return functions


def get_iam_users():
    users = iam.list_users()

    return [u["UserName"] for u in users["Users"]]


# ------------------------------------------------
# COLLECT FULL ACCOUNT OVERVIEW
# ------------------------------------------------

def get_account_overview():

    overview = {
        "timestamp": str(datetime.utcnow()),
        "region": REGION
    }

    try:
        overview["ec2_instances"] = get_ec2_data()
    except Exception as e:
        overview["ec2_error"] = str(e)

    try:
        overview["s3_buckets"] = get_s3_data()
    except Exception as e:
        overview["s3_error"] = str(e)

    try:
        overview["rds_instances"] = get_rds_data()
    except Exception as e:
        overview["rds_error"] = str(e)

    try:
        overview["lambda_functions"] = get_lambda_data()
    except Exception as e:
        overview["lambda_error"] = str(e)

    try:
        overview["iam_users"] = get_iam_users()
    except Exception as e:
        overview["iam_error"] = str(e)

    return overview


# ------------------------------------------------
# CALL CLAUDE
# ------------------------------------------------

def ask_claude(question, aws_data):

    prompt = f"""
You are an AWS Cloud Architect assistant.

Below is the AWS account inventory data.

AWS ACCOUNT DATA:
{aws_data}

User Question:
{question}

Analyze the infrastructure and answer clearly.
If possible, give insights and observations.
"""

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 700,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(payload),
        contentType="application/json",
        accept="application/json"
    )

    body = json.loads(response["body"].read())

    return body["content"][0]["text"]


# ------------------------------------------------
# RESPONSE FORMAT
# ------------------------------------------------

def response_json(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        },
        "body": json.dumps(body)
    }


# ------------------------------------------------
# LAMBDA HANDLER
# ------------------------------------------------

def lambda_handler(event, context):

    try:
        method = event.get("requestContext", {}).get("http", {}).get("method")

        # CORS
        if method == "OPTIONS":
            return response_json(200, {})

        body = json.loads(event.get("body", "{}"))
        user_message = body.get("message")

        if not user_message:
            return response_json(400, {"error": "Message required"})

        # ----------------------------------------
        # READ ENTIRE AWS ACCOUNT (READ ONLY)
        # ----------------------------------------
        account_data = get_account_overview()

        # Send to Claude
        reply = ask_claude(
            user_message,
            json.dumps(account_data, indent=2)
        )

        return response_json(200, {"reply": reply})

    except Exception as e:
        print("ERROR:", str(e))

        return response_json(500, {
            "error": "Internal Server Error",
            "details": str(e)
        })
