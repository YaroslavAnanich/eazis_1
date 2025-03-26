from fastapi import APIRouter

from src.api.dictionary import router as dictionary_router

main_router = APIRouter()

main_router.include_router(dictionary_router)