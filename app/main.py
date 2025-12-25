from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.orders import router as order_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend
        "http://127.0.0.1:3000",  # Альтернативный адрес
        "https://example.com",  # Продакшен
    ],  # Разрешенные источники
    allow_credentials=True,  # Разрешить куки
    allow_methods=["*"],  # Разрешить все методы (GET, POST, etc.)
    allow_headers=["*"],  # Разрешить все заголовки
)


@app.get("/")
async def root():
    return {"message": "Hello, world!"}


app.include_router(auth_router)
app.include_router(order_router)
