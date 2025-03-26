from typing import Dict, Any
from pydantic import BaseModel

class DictionaryCreateScheme(BaseModel):
    text: str

class DictionarySaveScheme(BaseModel):
    dictionary: Dict[str, Any]  # Указываем, что это словарь
    file_name: str = "dictionary.json"