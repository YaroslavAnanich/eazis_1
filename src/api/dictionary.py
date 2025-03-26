from fastapi import APIRouter, HTTPException

from src.classes.dictionary_worker import DictionaryWorker
from src.schemas.dictionary_scheme import DictionaryCreateScheme, DictionarySaveScheme

router = APIRouter()


dictionary_creator = DictionaryWorker()

@router.post("/create-dictionary")
async def create_dictionary(dictionary_create_scheme: DictionaryCreateScheme):
    try:
        return dictionary_creator.create_dictionary(dictionary_create_scheme.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании файла: {str(e)}")


@router.post("/save-dictionary")
async def save_dictionary(dictionary_save_scheme: DictionarySaveScheme):
    try:
        return dictionary_creator.save_dictionary_file(dictionary_save_scheme.dictionary, dictionary_save_scheme.file_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении файла: {str(e)}")


@router.get("/load-dictionary")
async def load_dictionary(file_path: str = "dictionary.json"):
    try:
        return dictionary_creator.load_dictionary_file(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке словаря: {str(e)}")


@router.delete("/delete-dictionary")
async def load_dictionary(file_path: str = "dictionary.json"):
    try:
        return dictionary_creator.delete_dictionary_file(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке словаря: {str(e)}")

@router.delete("/test")
async def load_dictionary():
    dc = DictionaryWorker()

    # Загружаем существующий словарь
    dictionary = dc.load_dictionary_file("dictionary.json")

    # Добавляем новую словоформу для леммы "have" (прошедшее время)
    dictionary = dc.add_word_form_by_tag(dictionary, "have", "VBD")  # Добавит "had"

    # Добавляем новую словоформу для леммы "change" (причастие настоящего времени)
    dictionary = dc.add_word_form_by_tag(dictionary, "change", "VBG")  # Добавит "changing"

    # Добавляем словоформу вручную
    dictionary = dc.add_word_form(dictionary, "have", "having")

    # Сохраняем обновленный словарь
    dc.save_dictionary_file(dictionary, "dictionary.json")