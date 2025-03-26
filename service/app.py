from fastapi import FastAPI, HTTPException
import nltk

from schemes import DictionaryCreateScheme, DictionarySaveScheme

from dictionary import DictionaryCreater, DictionaryWorker

# Загрузка необходимых ресурсов NLTK

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('words')

app = FastAPI()
dictionary_creator = DictionaryCreater()
dictionary_worker = DictionaryWorker()



@app.post("/create-dictionary")
async def create_dictionary(dictionary_create_scheme: DictionaryCreateScheme):
    try:
        return dictionary_creator.create_dictionary(dictionary_create_scheme.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании файла: {str(e)}")


@app.post("/save-dictionary")
async def save_dictionary(dictionary_save_scheme: DictionarySaveScheme):
    try:
        return dictionary_worker.save_dictionary_file(dictionary_save_scheme.dictionary, dictionary_save_scheme.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении файла: {str(e)}")


@app.get("/load-dictionary")
async def load_dictionary(file_path: str = "../saved_dictionaries/dictionary.json"):
    try:
        return dictionary_worker.load_dictionary_file(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке словаря: {str(e)}")


@app.delete("/delete-dictionary")
async def load_dictionary(file_path: str = "../saved_dictionaries/dictionary.json"):
    try:
        return dictionary_worker.delete_dictionary_file(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке словаря: {str(e)}")