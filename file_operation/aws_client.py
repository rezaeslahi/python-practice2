from typing import Any, List, Dict
from boto3 import client
from botocore.exceptions import ClientError
from botocore.client import BaseClient
from mypy_boto3_s3 import S3Client
from file_operation.config import ConfigParam, get_config
import logging
import pickle

_s3_client:S3Client|None = None

def _create_s3_client():
    global _s3_client
    config = get_config()
    try:
        _s3_client = client("s3",endpoint_url=config.local_stack_url,region_name=config.region_name,aws_access_key_id="test",aws_secret_access_key="test")
    except ClientError as e:
        logging.error(e)

def get_s3_cliet():
    if not _s3_client:
        _create_s3_client()
    return _s3_client

def create_bucket():
    config = get_config()
    s3_client = get_s3_cliet()
    try:
        s3_client.create_bucket(Bucket=config.bucket_name,CreateBucketConfiguration={"LocationConstraint": config.region_name})
    except ClientError as e:
        logging.error(e)


def put_object_on_s3(obj:Any,key:str):
    config = get_config()
    s3_client = get_s3_cliet()
    data:bytes = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
    s3_client.put_object(Bucket=config.bucket_name,Key=key,Body=data)

def get_object_from_s3(key:str)->Any:
    config = get_config()
    s3_client = get_s3_cliet()
    resp = s3_client.get_object(Bucket=config.bucket_name,Key=key)
    data:bytes = resp.get("Body").read()
    obj:Any = pickle.loads(data)
    return obj

def remove_bucket()->None:
    empty_bucket()
    config = get_config()
    s3_client = get_s3_cliet()    
    s3_client.delete_bucket(Bucket=config.bucket_name)

def list_keys(prefix:str="")->List[str]:
    config = get_config()
    s3_client = get_s3_cliet()
    resp:Dict[str,Any] = s3_client.list_objects_v2(Bucket=config.bucket_name,Prefix=prefix)
    contents = resp.get("Contents",[])
    return [c["Key"] for c in contents]

def delete_object(key:str):
    config = get_config()
    s3_client = get_s3_cliet()
    s3_client.delete_object(Bucket=config.bucket_name,Key=key)

def empty_bucket()->None:
    
    keys = list_keys()
    for key in keys:
        delete_object(key)  

def empty_bucket_paginated() -> None:
    config = get_config()
    bucket_name = config.bucket_name
    s3 = get_s3_cliet()
    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=bucket_name):
        objects = page.get("Contents", [])
        if not objects:
            continue

        delete_payload = {
            "Objects": [{"Key": obj["Key"]} for obj in objects]
        }

        s3.delete_objects(Bucket=bucket_name, Delete=delete_payload)


def delete_bucket() -> None:
    config = get_config()
    bucket_name = config.bucket_name
    s3 = get_s3_cliet()
    empty_bucket_paginated()
    s3.delete_bucket(Bucket=bucket_name)  
