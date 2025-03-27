from typing import Dict, Any
from pydantic import BaseModel

class DictionaryCreateScheme(BaseModel):
    text: str

class DictionarySaveScheme(BaseModel):
    dictionary: Dict[str, Any]  # Указываем, что это словарь
    file_name: str = "dictionary.json"

class DictionaryDeleteScheme(BaseModel):
    file_path: str = "dictionary.json"

class DictionaryAddWordScheme(BaseModel):
    dictionary: Dict[str, Any]  # Указываем, что это словарь
    lemma: str
    word_form: str


