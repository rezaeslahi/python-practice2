import json
from typing import List,Dict,Any
from dataclasses import dataclass,asdict
from pydantic import BaseModel, Field
# ---------------------------------------------------------------------------
# [1] Define JSON in code
# Purpose: Show how to represent JSON objects/arrays directly as Python dict/list.
# Summary: JSON object == Python dict; JSON array == Python list; JSON values map naturally.
# ---------------------------------------------------------------------------
def define_json_in_code()->Dict[str,Any]:
    """
    Defining JSON in the code
    """

    payload:Dict[str,Any] = {
        "request_id":"req-123",
        "user":{"id":42,"name":"Reza"},
        "flags":{"debug":True,"dry_run":False},
        "scores":[0.91,0.12,0.777],
        "optional":None,
        "metadata":[{"k":"team","v":"ai"},{"k":"level","v":"senior"}],
    }
    return payload

# ---------------------------------------------------------------------------
# [2] Serialize JSON to string using json.dumps
# Purpose: Convert Python dict/list -> JSON text (str).
# Summary: Use this when you want a JSON string (e.g., send over HTTP, logs, caching).
# ---------------------------------------------------------------------------
def s02_to_json_string(payload:Dict[str,Any])->str:
    """
    Use this when you want a JSON string (e.g., send over HTTP, logs, caching).
    """
    json_text:str = json.dumps(payload,indent=4,sort_keys=True,ensure_ascii=False)
    return json_text

# ---------------------------------------------------------------------------
# [3] Parse JSON string using json.loads
# Purpose: Convert JSON text (str/bytes/bytearray) -> Python dict/list.
# Summary: This is your "JSON -> Python object" entry point for strings.
# ---------------------------------------------------------------------------
def s03_from_json_string(json_text:str)->Dict[str,Any]:
    parsed:Any = json.loads(json_text)

    if not isinstance(parsed,dict):
        raise ValueError("Expected json object to be dict")
    
    payload:Dict[str,Any] = parsed
    return payload

# ---------------------------------------------------------------------------
# [4] Map an object to JSON (dataclass -> dict -> JSON string)
# Purpose: Demonstrate object -> JSON workflow without overengineering.
# Summary: Use dataclass + asdict for easy "object to JSON-friendly dict".
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class UserProfile():
    user_id:int
    name:str
    tags:List[str]
    is_active:bool

def s04_object_to_json_string(profile:UserProfile)->str:
    """
    Use dataclass + asdict for easy "object to JSON-friendly dict".
    """
    obj_dic:Dict[str,Any] = asdict(profile)
    json_text:str = json.dumps(obj_dic,indent=4,sort_keys=True)
    return json_text

# ---------------------------------------------------------------------------
# [4.1] Map an object to JSON Using Object encoder
# Purpose: Demonstrate object -> JSON workflow without overengineering.
# Summary: Use "default" attribute of dumps to pass the encoder function.
# ---------------------------------------------------------------------------
def user_profile_encoder(profile:UserProfile)->Dict[str,Any]:
    if not isinstance(profile,UserProfile):
        raise ValueError("UserProfile expected")
    obj_dic = {
        "user_id":profile.user_id,
        "name":profile.name,
        "tags":profile.tags,
        "is_active":profile.is_active
    }
    # obj_dic = profile.__dict__
    # obj_dic = asdict(profile)
    return obj_dic

def s04_1_object_to_json_string(profile:UserProfile)->str:
    json_text = json.dumps(profile,default=user_profile_encoder,indent=4,sort_keys=True)
    return json_text


# ---------------------------------------------------------------------------
# [5] Map JSON to an object (dict -> dataclass)
# Purpose: Show safe parsing from Dict[str, Any] into a typed object.
# Summary: Validate required fields; convert types; then construct object.
# ---------------------------------------------------------------------------
def s05_json_dict_to_user_profile(data:Dict[str,Any])->UserProfile:
    user_id = data.get("user_id")
    name = data.get("name")
    tags = data.get("tags")
    is_active = data.get("is_active")
    if not isinstance(user_id,int):
        raise ValueError("")
    if not isinstance(name,str):
        raise ValueError("")
    if not isinstance(tags,list) or any(not isinstance(x,str) for x in tags):
        raise ValueError("")
    if not isinstance(is_active,bool):
        raise ValueError("")
    profile:UserProfile = UserProfile(user_id,name,tags,is_active)
    return profile

def s05_1_json_dict_to_user_profile(data:Dict[str,Any])->UserProfile:
    profile:UserProfile = UserProfile(**data)
    return profile

# ---------------------------------------------------------------------------
# [6] Write JSON to a file using json.dump
# Purpose: Serialize Python object -> JSON and stream directly to file.
# Summary: Use json.dump when you already have a file handle (no intermediate string).
# ---------------------------------------------------------------------------

def s06_write_json_file(path:str,payload:Dict[str,Any])->None:
    with open(path,"w",encoding="utf-8") as file:
        json.dump(payload,file,indent=4)

# ---------------------------------------------------------------------------
# [7] Read JSON file using json.load
# Purpose: Deserialize JSON file -> Python dict/list.
# Summary: Use json.load when reading from file handles.
# ---------------------------------------------------------------------------
def s07_read_json_file(path:str)->Dict[str,Any]:
    parsed:Any = None
    with open(path,"r", encoding="utf-8") as file:
        parsed = json.load(file)
    if not parsed or not isinstance(parsed,dict):
        raise ValueError("")
    payload:Dict[str,Any] = parsed
    return payload

# ---------------------------------------------------------------------------
# [12] Pydantic BaseModel <-> JSON
# Purpose: Show the cleanest "JSON <-> typed object" approach for interviews.
# Summary: Pydantic validates types; can parse dict/JSON and export dict/JSON.
# ---------------------------------------------------------------------------

class UserProfileModel(BaseModel):
    user_id:int = Field(...,ge=1)  
    name:str = Field(...,)
    tags:List[str] = Field(default_factory=list)
    is_active:bool = Field(default=True)

def s12_pydantic_json_roundtrip_example()->None:
    incoming_dict: Dict[str, Any] = {
        "user_id": 7,
        "name": "Reza",
        "tags": ["ml", "rag"],
        "is_active": True,
    }
    # Dict -> model (validated)
    model_from_dict: UserProfileModel = UserProfileModel.model_validate(incoming_dict)

    # Model -> dict (JSON-like)
    outgoing_dict:Dict[str,Any] = model_from_dict.model_dump()

    # Model -> JSON string
    outgoing_json:str = model_from_dict.model_dump_json(indent=4)

    # JSON string -> model (validated)
    model_from_json_str = UserProfileModel.model_validate_json(outgoing_json)

    pass

def main():
    print("Running....")
        
    profile:UserProfile = UserProfile(user_id=10,name="Reza,",tags=["AI","ML"],is_active=True)
    obj_json_txt:str = s04_1_object_to_json_string(profile=profile)
    data:Dict[str,Any] = s03_from_json_string(obj_json_txt)
    s06_write_json_file("JSON/profile.json",data)
    data2 = s07_read_json_file("JSON/profile.json") 
    print(f"data2:{data2}")
    s12_pydantic_json_roundtrip_example()




if __name__ == "__main__":
    main()