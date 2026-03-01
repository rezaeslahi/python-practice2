from dataclasses import dataclass
import os

@dataclass
class ConfigParam():
    chunk_size:int
    chunk_overlap:int
    line_buffer_size:int
    chunk_key_prefix:str
    
    pdf_file_key_prefix:str
    text_file_key_prefix:str

    local_stack_url:str
    region_name:str
    bucket_name:str

_config:ConfigParam|None = None

def create_config()->None:
    global _config
    if not _config:
        chunk_size:int = os.getenv("CHNK_SIZE",600)
        chunk_overlap:int = os.getenv("CHNK_OVERLAP",10)
        line_buffer_size:int = os.getenv("LINE_BUFFER_SIZE", 20)
        chunk_key_prefix:str = os.getenv("CHUNK_KEY_PREFIX", "CHUNK")
        
        pdf_file_key_prefix:str = os.getenv("PDF_FILE_KEY_PREFIX", "PDF")
        text_file_key_prefix:str = os.getenv("TEXT_FILE_KEY_PREFIX", "TEXT")

        local_stack_url:str = os.getenv("LOCAL_STACK_URL", "http://localhost:4566")
        region_name:str = os.getenv("REGION_NAME", "eu-west-2")
        bucket_name:str = os.getenv("BUCKET_NAME", "sample-bucket")

        _config = ConfigParam(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            line_buffer_size=line_buffer_size,
            chunk_key_prefix = chunk_key_prefix,            
            pdf_file_key_prefix=pdf_file_key_prefix,
            text_file_key_prefix=text_file_key_prefix,
            local_stack_url=local_stack_url,
            region_name=region_name,
            bucket_name=bucket_name)
        
def get_config()->ConfigParam:
    if not _config:
        raise RuntimeError("Config is not yet set")
    return _config
    

