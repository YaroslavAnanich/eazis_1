from fastapi import APIRouter, HTTPException

from src.classes.dictionary_worker import DictionaryWorker
from src.schemas.dictionary_response_schemes import DictionaryCreateResponseScheme, DictionarySaveResponseScheme, \
    DictionaryLoadResponseScheme, DictionaryDeleteResponseScheme, DictionaryAddWordFormResponseScheme, \
    DictionaryListDictionariesResponseScheme
from src.schemas.dictionary_schemes import (DictionaryCreateScheme, DictionarySaveScheme,
                                            DictionaryAddWordScheme, DictionaryDeleteScheme)

router = APIRouter()


dictionary_worker = DictionaryWorker()

@router.post("/create-dictionary", response_model=DictionaryCreateResponseScheme)
async def create_dictionary(dictionary_create_scheme: DictionaryCreateScheme):
    try:
        return {"dictionary": dictionary_worker.create_dictionary(dictionary_create_scheme.text)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании файла: {str(e)}")


@router.post("/save-dictionary", response_model=DictionarySaveResponseScheme)
async def save_dictionary(dictionary_save_scheme: DictionarySaveScheme):
    try:
        return {"message": dictionary_worker.save_dictionary_file(dictionary_save_scheme.dictionary, dictionary_save_scheme.file_name)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении файла: {str(e)}")


@router.get("/list-dictionaries", response_model=DictionaryListDictionariesResponseScheme)
async def list_dictionaries():
    try:
        return {"dictionaries": dictionary_worker.list_dictionary_files()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении списка существующих словарей: {str(e)}")


@router.get("/load-dictionary", response_model=DictionaryLoadResponseScheme)
async def load_dictionary(file_path: str = "dictionary.json"):
    try:
        return {"dictionary": dictionary_worker.load_dictionary_file(file_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке словаря: {str(e)}")


@router.delete("/delete-dictionary", response_model=DictionaryDeleteResponseScheme)
async def delete_dictionary(dictionary_save_scheme: DictionaryDeleteScheme):
    try:
        return {"message": dictionary_worker.delete_dictionary_file(dictionary_save_scheme.file_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении словаря: {str(e)}")


@router.post("/add-word-form", response_model=DictionaryAddWordFormResponseScheme)
async def add_word(dictionary_add_scheme: DictionaryAddWordScheme):
    dictionary = dictionary_add_scheme.dictionary
    lemma = dictionary_add_scheme.lemma
    word_form = dictionary_add_scheme.word_form

    try:
        return {"dictionary": dictionary_worker.add_word_form(dictionary, lemma, word_form)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении словоформы: {str(e)}")
