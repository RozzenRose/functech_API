from fastapi import FastAPI, Request
from app.routers.auth import router as auth_router
from app.routers.orders import router as order_router
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address


limiter = Limiter(key_func=get_remote_address)
app = FastAPI()


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


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
@limiter.limit("1/minute")
async def root(request: Request):
    return {"message": "Hello, world!"}


app.include_router(auth_router)
app.include_router(order_router)
