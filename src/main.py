from fastapi import FastAPI
import nltk

# Загрузка ресурсов ДО импорта других модулей
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('wordnet')
nltk.download('words')

from src.api.routers import main_router

app = FastAPI()
app.include_router(main_router)

