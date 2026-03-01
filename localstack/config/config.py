from dataclasses import dataclass
from dotenv import load_dotenv
import os

@dataclass(frozen=True)
class LocalStackConfig():
    url:str
    region:str
    secret_key:str
    access_key:str


def load_config()->LocalStackConfig:
    load_dotenv()
    url:str = os.getenv("URL","http://localhost:4566")
    region:str = os.getenv("RGION","eu-west-1")
    secret_key:str = os.getenv("SECRET_KEY","test")
    access_key:str = os.getenv("ACCESS_KEY","test")
    config = LocalStackConfig(url=url,region=region,secret_key=secret_key,access_key=access_key)
    return config
