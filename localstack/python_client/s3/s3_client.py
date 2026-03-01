import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from localstack.config.config import LocalStackConfig, load_config
from enum import Enum
import logging
from typing import List, Dict,Any, BinaryIO, Optional
from mypy_boto3_s3 import S3Client
from pathlib import Path
import threading
import sys
import os
from io import BytesIO


class CallBackClass():
    def __call__(self, *args, **kwds):
        pass

class Services(str,Enum):
    s3 = "s3"



def make_s3_client(config:LocalStackConfig)->S3Client:
    s3_client:S3Client = None
    try:
        
        s3_client = boto3.client(
        service_name=Services.s3,
        endpoint_url=config.url,
        region_name=config.region,
        aws_access_key_id=config.access_key,
        aws_secret_access_key=config.secret_key
    )
    except ClientError as e:
        logging.error(e)
    return s3_client

def create_s3_bucket(s3_client:S3Client,bucket_name:str,config:LocalStackConfig)->None:
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return
    except ClientError as e:
        logging.error(e)   
    try:
        s3_client.create_bucket(Bucket=bucket_name,CreateBucketConfiguration={"LocationConstraint": config.region})
    except ClientError as e:
        logging.error(e)

def get_bucket_list(s3_client:S3Client)->List[str]:
    resp:Dict[str,Any] = s3_client.list_buckets()        
    bucket_names:List[str] = [b.get("Name") for b in resp.get("Buckets")]
    return bucket_names

def put_text(s3_client:S3Client, bucket_name:str,key:str,text:str)->None:
    s3_client.put_object(Bucket=bucket_name,Key=key,Body=text.encode("utf-8"),ContentType="text")

def get_text(s3_client:S3Client,bucket_name:str,key:str)->str:
    resp:Dict[str,Any] = s3_client.get_object(Bucket=bucket_name,Key=key)
    body = resp.get("Body").read()
    text = body.decode("utf-8")
    return text

def list_keys(s3_client:S3Client,bucket_name:str, prefix:str = "")->List[str]:
    resp:Dict[str,Any] = s3_client.list_objects_v2(Bucket=bucket_name,Prefix=prefix)
    contents = resp.get("Contents",[])
    keys = [c["Key"] for c in contents]
    return keys

def delete_key(s3_cleint:S3Client,bucket_name:str,key:str)->None:
    s3_cleint.delete_object(Bucket=bucket_name,Key=key)

def upload_file(s3_client:S3Client,bucket:str,key:str,filePath:Path,callBack:CallBackClass = None)->None:
    s3_client.upload_file(Filename=str(filePath),Bucket=bucket,Key=key,Callback=callBack)

def download_file(s3_client:S3Client, bucket:str, key:str, dest:Path,callback:CallBackClass = None)->None:
    dest.parent.mkdir(exist_ok=True,parents=True)
    s3_client.download_file(Bucket=bucket,Key=key,Filename=str(dest),Callback=callback)


def upload_fileobj(
    s3: S3Client,bucket: str,key: str,fileobj: BinaryIO,callback: CallBackClass = None) -> None:
    """
    High-level upload that reads from an already-open file-like object (BinaryIO).
    Useful when you don't have a real file path (streaming, in-memory, etc.).
    """
    extra_args: dict[str, Any] = {"ContentType": "application/octet-stream"}
    s3.upload_fileobj(
        Fileobj=fileobj,
        Bucket=bucket,
        Key=key,
        ExtraArgs=extra_args,
        Callback=callback,
    )

def download_fileobj(s3: S3Client,bucket: str,key: str,fileobj: BinaryIO,callback: CallBackClass = None) -> None:
    """
    High-level download into an already-open writable file-like object.
    Useful for in-memory buffers, streaming responses, etc.
    """
    s3.download_fileobj(
        Bucket=bucket,
        Key=key,
        Fileobj=fileobj,
        Callback=callback,
    )

def list_all_keys_paginated(
    s3: S3Client,
    bucket: str,
    prefix: str = "",
) -> list[str]:
    keys: list[str] = []
    continuation_token: Optional[str] = None

    while True:
        kwargs: dict[str, Any] = {"Bucket": bucket, "Prefix": prefix}
        if continuation_token is not None:
            kwargs["ContinuationToken"] = continuation_token

        resp: dict[str, Any] = s3.list_objects_v2(**kwargs)

        contents = resp.get("Contents", [])
        for obj in contents:
            key = obj.get("Key")
            if isinstance(key, str):
                keys.append(key)

        is_truncated = bool(resp.get("IsTruncated", False))
        if not is_truncated:
            break

        next_token = resp.get("NextContinuationToken")
        if not isinstance(next_token, str) or not next_token:
            # Defensive: avoid infinite loop if API response is unexpected
            break

        continuation_token = next_token

    return keys


def safe_head_object(s3: BaseClient, bucket: str, key: str) -> bool:
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        code = _err_code(e)
        if code in {"404", "NoSuchKey", "NotFound"}:
            return False
        raise
def _err_code(e: ClientError) -> str:
    # Common pattern: AWS error codes are in e.response["Error"]["Code"]
    return str(e.response.get("Error", {}).get("Code", ""))

class UploadProgressCallBack(CallBackClass):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()
class GeneralProgressCallBack(CallBackClass):
    def __init__(self,filename):
        self.total = 0
        self.filename = filename
    def __call__(self, bytes:int):
        self.total += bytes
        print(f"{self.filename}: +{bytes} bytes (total={self.total})")
        


def main():
    print("Running...")
    config:LocalStackConfig = load_config()
    s3_client:S3Client = make_s3_client(config)
    # create_s3_bucket(s3_client,"bucket1",config)
    # create_s3_bucket(s3_client,"bucket2",config)
    # bucket_names = get_bucket_list(s3_client)
    # print(bucket_names)
    # put_text(s3_client=s3_client,bucket_name="bucket1",key="FirstText",text="Here is my first text")
    # text = get_text(s3_client=s3_client,bucket_name="bucket1",key="FirstText")
    # print(text)
    # keys = list_keys(s3_client,"bucket1")
    # print(f"keys: {keys}")
    delete_key(s3_client,"bucket1","profileJSON")

    file_to_upload = Path("localstack/python_client/s3/files/upload/profile.json")
    dest = Path("localstack/python_client/s3/files/download/downloded.json")

    upload_progress_call_back:CallBackClass = GeneralProgressCallBack(str(file_to_upload))
    download_progress_call_back:CallBackClass = GeneralProgressCallBack(str(dest))

    # upload_file(s3_client,"bucket1","profileJSON",file_to_upload,callBack=upload_progress_call_back)
    # download_file(s3_client,"bucket1","profileJSON",dest,callback=download_progress_call_back)

    with file_to_upload.open("rb") as file:
        upload_fileobj(s3_client,"bucket1","profileJSON",file,callback=upload_progress_call_back)
    buf = BytesIO()
    download_fileobj(s3_client,"bucket1","profileJSON",buf,callback=download_progress_call_back)
    print("download_fileobj bytes:", len(buf.getvalue()))

    pass

if __name__ == "__main__":
    main()

    
    
