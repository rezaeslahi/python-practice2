from pathlib import Path
from typing import List,Any,Iterator,Optional
import pickle
import pymupdf
from dataclasses import dataclass

#------------------------------------------------------------
##  Write Text Files
#------------------------------------------------------------
def write_text_in_file(file_path:Path,text:str,encoding:str = "utf-8")->None:    
    file_path.parent.mkdir(exist_ok=True,parents=True)
    with open(file_path,"w",encoding=encoding) as f:
        f.write(text)


#------------------------------------------------------------
##  Read Text Files
#------------------------------------------------------------
def read_text_file(file_path:Path,encoding:str = "utf-8")->str:
    text:str
    with open(file_path,"r",encoding=encoding) as file:
        text = file.read()
    return text

#------------------------------------------------------------
##  Read Lines from Text Files
#------------------------------------------------------------
def read_text_file_lines(file_path:Path,encoding:str="utf-8")->List[str]:
    lines:List[str] = []
    with open(file_path,"r",encoding=encoding) as file:
        for line in file:
            lines.append(line.strip())
    return lines

#------------------------------------------------------------
##  pickle object, SAVE
#------------------------------------------------------------
def save_pickle(file_path:Path,obj:Any):
    file_path.parent.mkdir(exist_ok=True,parents=True)
    with open(file_path,"wb") as file:
        pickle.dump(obj,file,protocol=pickle.HIGHEST_PROTOCOL)

#------------------------------------------------------------
##  pickle object, LOAD
#------------------------------------------------------------
def load_pickle(file_path:Path,obj:Any)->Any:
    file_path.parent.mkdir(exist_ok=True,parents=True)
    with open(file_path,"rb") as file:
        obj = pickle.load(file_path)
    return obj


#------------------------------------------------------------
##  Copy big files in chunks
#------------------------------------------------------------
_MB = 1024 ** 2
def copy_files_in_chunk(src:Path,dest:Path, chunk_size:int = 8*_MB):
    dest.parent.mkdir(exist_ok=True,parents=True)
    with open(src,"rb") as fin , open(dest,"wb") as fout:
        while True:
            chunk = fin.read(chunk_size)
            if not chunk:
                break
            fout.write(chunk)

#------------------------------------------------------------
##  read line for big text files
#------------------------------------------------------------

def yield_line(file_path:Path, endocing:str)->Iterator[str]:
    with open(file_path,"r",encoding=endocing) as f:
        for line in f:
            yield line.strip()

def process_big_text_file(file_path,enoding:str = "utf-8")->List[str]:
    lines:List[str] = []
    itr = yield_line(file_path,enoding)
    for line in itr:
        lines.append(line)
    return lines


#------------------------------------------------------------
##  append to file
#------------------------------------------------------------
def append_text_line(file_path: Path, line: str, encoding: str = "utf-8") -> None:
    
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("a", encoding=encoding, newline="\n") as f:
        f.write(line + "\n")

@dataclass(frozen=True)
class pdfPageText():
    page_id:int
    text:str



def yield_pdf_page_text(file_path:Path, start:int = 0, end:Optional[int] = None)->Iterator[pdfPageText]:

    if not file_path.exists():
        raise FileNotFoundError("PDF file not found")
    if file_path.suffix.lower() != ".pdf":
        raise ValueError("File format error!")

    doc:pymupdf.Document
    try:
        doc = pymupdf.open(file_path)
        total_page:int = doc.page_count
        if not end:
            end = total_page
        for page_id in range(start,end):
            page:pymupdf.Page = doc.load_page(page_id)
            text:str = page.get_text("text")
            pdf_page_text = pdfPageText(page_id=page_id,text=text)
            yield pdf_page_text
    finally:
        doc.close()
    pass

def main():
    file_path = Path(__file__).parent / "files/text.txt"
    file_path2 = Path(__file__).parent / "files/text2.txt"
    # write_text_in_file(file_path,"write this\nAnd This\nGod please help me get Aurora job\nWhy??Same industry, aligned with what I am good at, and...\n It is in Oxford! I can make a greate life for my family")
    # print(read_text_file_lines(file_path))
    # copy_files_in_chunk(file_path,file_path2)
    print(process_big_text_file(file_path))
    pass

if __name__ == "__main__":
    main()
