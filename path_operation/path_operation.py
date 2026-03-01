from pathlib import Path
from typing import Dict,List


def build_common_paths()->Dict[str,Path]:
    this_file_path:Path = Path(__file__)
    cwd = Path.cwd()
    raw_data:Path = cwd / "raw_data"
    text_file_path = raw_data / "text_file.txt"

    out = {
        "this_file_path":this_file_path,
        "this_file_path_abs":this_file_path.resolve(),
        "cwd":Path.cwd(),
        "home":Path.home(),
        "relative_path_to_cwd":get_file_relative_path(Path.cwd()),
        "relative_path_to_root":get_file_relative_path(detect_project_root_with_marker(["project_root.txt"])),
        "text_file_path":text_file_path
    }
    return out

def create_folder_with_name(folder_name:str):
    root_project = detect_project_root_with_marker(["project_root.txt"])
    folder_path = root_project / folder_name
    folder_path.mkdir(exist_ok=True,parents=True)

def create_file_with_relative_path(file_path:str):
    root_project = detect_project_root_with_marker(["project_root.txt"])
    file_path:Path = root_project / file_path
    parent_path = file_path.parent
    parent_path.mkdir(parents=True,exist_ok=True)
    file_path.touch(exist_ok=True)
    

def get_file_relative_path(relative_to:Path)->Path:
    file_path = Path(__file__).resolve()    
    rel_path = file_path.relative_to(relative_to)
    return rel_path

def detect_project_root_with_marker(markers:List[str])->Path:
    current = Path(__file__).resolve()
    if current.is_file():
        current = current.parent
    while current.parent != current:
        for marker in markers:
            if (current / marker).exists():
                return current
            current = current.parent
        
    raise FileNotFoundError("Root not found!!")

def inspect_path(path:Path = None):
    if not path:
        path = Path(__file__).resolve()
    exists:bool = path.exists()
    is_file:bool = path.is_file()
    is_dir:bool = path.is_dir()
    name:str = path.name
    stem:str = path.stem
    suffix:str = path.suffix
    out = {
        "exists":exists,
        "is_file":is_file,
        "is_dir":is_dir,
        "name":name,
        "stem":stem,
        "suffix":suffix
    }
    return out

def find_patterns_in_path(root:Path,extension:str)->List[Path]:
    return [p for p in root.rglob(f"*{extension}") if p.is_file()]


def decent_dict_print(dict:Dict):
    for k,v in dict.items():
        print(f"({k}: {v})")

def main():
    # decent_dict_print(build_common_paths())
    # root_project = detect_project_root_with_marker(["project_root.txt"])
    # print(root_project)
    # create_folder_with_name("data/training")
    # create_file_with_relative_path("data/training/train.csv")
    # decent_dict_print(inspect_path())
    root_project = detect_project_root_with_marker(["project_root.txt"])
    print(find_patterns_in_path(root_project,".py"))


if __name__ == "__main__":
    main()