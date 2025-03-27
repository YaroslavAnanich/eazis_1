from pydantic import BaseModel
from typing import Dict, Any, List

class DictionaryCreateResponseScheme(BaseModel):
    dictionary: Dict[str, Any]

class DictionarySaveResponseScheme(BaseModel):
    message: str

class DictionaryLoadResponseScheme(BaseModel):
    dictionary: Dict[str, Any]

class DictionaryDeleteResponseScheme(BaseModel):
    message: str

class DictionaryAddWordFormResponseScheme(BaseModel):
    dictionary: Dict[str, Any]

class DictionaryListDictionariesResponseScheme(BaseModel):
    dictionaries: List[Any]