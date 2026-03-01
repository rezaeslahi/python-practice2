
from file_operation.config import ConfigParam,get_config,create_config

from typing import Iterator, List,AsyncIterator
from pathlib import Path
from itertools import count
import pymupdf
from file_operation import aws_client
import logging
import uuid
from datetime import datetime,timezone
from threading import Thread
import asyncio
import time
from threading import Thread
from asyncio import Semaphore


class DocumentPage():
    # it is memory friendly
    _doc_page_id_itr = count(start=0,step=1)
    def __init__(self,text:str,doc_ref:str,page_index:int|None = None):
        self.text = text
        self.doc_ref = doc_ref
        self.page_index = page_index
        self.id = next(self._doc_page_id_itr)

class Chunk():
    _chunk_id_itr = count(start=0)
    def __init__(self,text:str,doc_ref:str):
        self.text = text
        self.doc_ref = doc_ref
        self.id = next(self._chunk_id_itr)

async def process_doc_page_async(document_pages:Iterator[DocumentPage]):
    async for doc_page in document_pages:
        chunks:List[Chunk] = create_chunks(doc_page.text,doc_page.doc_ref)
        for chunk in chunks:
            chunk_key = create_unique_chunk_key(chunk)
            aws_client.put_object_on_s3(chunk,chunk_key)

def process_doc_page_sync(document_pages:Iterator[DocumentPage]):
    for doc_page in document_pages:
        chunks:List[Chunk] = create_chunks(doc_page.text,doc_page.doc_ref)
        for chunk in chunks:
            chunk_key = create_unique_chunk_key(chunk)
            aws_client.put_object_on_s3(chunk,chunk_key)
    


def paginate_large_pdf_file_sync(file_path:Path)->Iterator[DocumentPage]:
    try:
        doc_ref = create_pdf_doc_ref(file_path=file_path)
        doc:pymupdf.Document = pymupdf.open(file_path)
        total_pages = doc.page_count
        for page_index in range(total_pages):
            page: pymupdf.Page = doc.load_page(page_id=page_index)
            text:str = page.get_text("text")        
            doc_page = DocumentPage(text=text,doc_ref=doc_ref,page_index=page_index)
            yield doc_page
    except pymupdf.Exception as e:
        logging.error(e)
    finally:
        doc.close()

async def paginate_large_pdf_file_async(file_path:Path)->AsyncIterator[DocumentPage]:
    try:
        doc_ref = create_pdf_doc_ref(file_path=file_path)
        doc:pymupdf.Document = pymupdf.open(file_path)
        total_pages = doc.page_count
        for page_index in range(total_pages):
            page: pymupdf.Page = doc.load_page(page_id=page_index)
            text:str = page.get_text("text")        
            doc_page = DocumentPage(text=text,doc_ref=doc_ref,page_index=page_index)
            yield doc_page
    except Exception as e:
        logging.error(e)
    finally:
        doc.close()


def paginate_large_text_file_sync(file_path:Path)->Iterator[DocumentPage]:
    doc_ref = create_txt_doc_ref(file_path)
    config:ConfigParam = get_config()
    line_buffer:List[str] = []

    with open(file_path,"r",encoding="utf-8") as file:
        lines = 0
        page_index = 0
        for line in file:
            line_buffer.append(line.strip())
            lines += 1
            if lines == config.line_buffer_size:
                text = "\n".join(line_buffer)
                doc_page = DocumentPage(text=text,doc_ref=doc_ref,page_index=page_index)
                page_index += 1
                lines = 0
                line_buffer.clear()
                yield doc_page

async def paginate_large_text_file_async(file_path:Path)->AsyncIterator[DocumentPage]:
    doc_ref = create_txt_doc_ref(file_path)
    config:ConfigParam = get_config()
    line_buffer:List[str] = []

    with open(file_path,"r",encoding="utf-8") as file:
        lines = 0
        page_index = 0
        for line in file:
            line_buffer.append(line.strip())
            lines += 1
            if lines == config.line_buffer_size:
                text = "\n".join(line_buffer)
                doc_page = DocumentPage(text=text,doc_ref=doc_ref,page_index=page_index)
                page_index += 1
                lines = 0
                line_buffer.clear()
                yield doc_page
                
async def ingest_documents_async(pdf_files:List[Path] = [], text_files:List[Path] = []):
    
    aws_client.create_bucket()

    # for pdf_file in pdf_files:
    #     paginated_pdf:AsyncIterator[DocumentPage] = paginate_large_pdf_file_async(pdf_file)
    #     await process_doc_page_async(paginated_pdf)
            
    # for text_file in text_files:
    #     paginated_txt:AsyncIterator[DocumentPage] = paginate_large_text_file_async(text_file)
    #     await process_doc_page_async(paginated_txt)

    for pdf_file in pdf_files:
        paginated_pdf:Iterator[DocumentPage] = paginate_large_pdf_file_sync(pdf_file)
        process_doc_page_sync(paginated_pdf)
    for text_file in text_files:
        paginated_txt:Iterator[DocumentPage] = paginate_large_text_file_sync(text_file)
        process_doc_page_sync(paginated_txt)


def ingest_documents_multi_thread(pdf_files:List[Path] = [], text_files:List[Path] = []):
    
    aws_client.create_bucket()

    threads = [Thread(target=paginate_large_pdf_file_sync,args=(pdf_file,)) for pdf_file in pdf_files]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    
    for text_file in text_files:
        paginated_txt:Iterator[DocumentPage] = paginate_large_text_file_sync(text_file)
        process_doc_page_sync(paginated_txt)
    


def create_chunks(large_text:str,doc_ref:str)->List[Chunk]:
    chunks:List[Chunk] = []
    config = get_config()
    n = len(large_text)
    i = 0
    is_end = False
    while i<n and not is_end:
        j = min(n,i+config.chunk_size)
        chunk_text = large_text[i:j]
        chunk = Chunk(text=chunk_text,doc_ref=doc_ref)
        chunks.append(chunk)
        if j == n:
            is_end = True
            continue
        i = j - config.chunk_overlap
    return chunks

def create_unique_chunk_key(chunk:Chunk)->str:
    config = get_config()
    chunk_key = uuid_generator(prefix=config.chunk_key_prefix)
    return chunk_key

def create_pdf_doc_ref(file_path:Path)->str:
    config = get_config()
    pdf_key = uuid_generator(prefix=config.pdf_file_key_prefix,suffix=file_path.name)
    return pdf_key

def create_txt_doc_ref(file_path:Path)->str:
    config = get_config()
    txt_key = uuid_generator(prefix=config.text_file_key_prefix,suffix=file_path.name)
    return txt_key

def uuid_generator(prefix:str="",suffix:str="")->str:
    time:str = str(datetime.now())
    id:int = uuid.uuid4().hex[0:8]
    output = f"{prefix}/{id}_{time}_{suffix}"
    return output

async def main():
    
    create_config()
    aws_client.delete_bucket()
    allowed_suffix = {".pdf"}
    pdf_folder = Path(__file__).relative_to(Path.cwd()).parent / "files/rag_docs"
    pdfs = [p for p in pdf_folder.rglob("*.pdf") if p.suffix.lower() in allowed_suffix]
    start = time.perf_counter()
    await ingest_documents_async(pdf_files=pdfs)
    end = time.perf_counter()
    total_time = end - start
    print(f"Run Time:{total_time}")
    keys = aws_client.list_keys()
    for key in keys:
        print(f"Key:{key}")
    print(f"len:{len(key)}")

if __name__ == "__main__":
    asyncio.run(main())
    