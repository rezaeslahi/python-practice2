from fastapi import HTTPException, status, APIRouter
from pydantic import BaseModel,Field
from typing import List

class ObjectModel(BaseModel):
    pass
class IngestionObjectModel(BaseModel):
    objs:List[ObjectModel] = Field(default_factory=[])


router = APIRouter(prefix="/This_Router",tags=["This_router"])

@router.get("/service/{obj_id}",response_model=List[ObjectModel])
def get_object(doc_id:int)->List[ObjectModel]:
    pass

@router.post("/service/ingest")
def ingest_objects(objs:IngestionObjectModel)->List[ObjectModel]:
    pass