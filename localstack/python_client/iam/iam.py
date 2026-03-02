from __future__ import annotations

import json
from typing import cast

import boto3
from mypy_boto3_iam import IAMClient


def make_iam_client() -> IAMClient:
    client = boto3.client(
        "iam",
        endpoint_url="http://localhost:4566",  # for LocalStack
        region_name="eu-west-2",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )
    return cast(IAMClient, client)


def create_s3_policy(iam: IAMClient, bucket_name: str) -> str:
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:ListBucket"],
                "Resource": f"arn:aws:s3:::{bucket_name}",
            },
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:PutObject"],
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
            },
        ],
    }

    response = iam.create_policy(
        PolicyName=f"{bucket_name}-access-policy",
        PolicyDocument=json.dumps(policy_document),
    )

    return response["Policy"]["Arn"]


def create_role(iam: IAMClient, role_name: str) -> None:
    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }

    iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(assume_role_policy),
    )


def attach_policy_to_role(iam: IAMClient, role_name: str, policy_arn: str) -> None:
    iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_arn,
    )

def main():
    iam = make_iam_client()
    policy_arn = create_s3_policy(iam, "interview-bucket")
    create_role(iam, "s3-access-role")
    attach_policy_to_role(iam, "s3-access-role", policy_arn)