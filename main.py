import uvicorn
from celery import Celery
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from ecommerce import config
from ecommerce.auth import router as auth_router

from ecommerce.cart import router as cart_router
from ecommerce.db import database
from ecommerce.orders import router as order_router
from ecommerce.products import router as product_router
from ecommerce.user import router as user_router
from ecommerce.root import router as root_router


from fastapi_pagination import add_pagination

description = """
Ecommerce API

## Users

You will be able to:

* **Create users** 
* **Read users** 
"""


app = FastAPI(
    title="EcommerceApp",
    description=description,
    version="0.0.1",
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "Mukul Mantosh",
        "url": "https://x-force.example.com/contact/",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)


add_pagination(app)
origins = [
    "http://localhost",
    "http://localhost:8000",
]


app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow only the specific server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Authentication
API_KEY = config.XAPIKEY


@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    api_key = request.cookies.get("x-api-key")
    if api_key != API_KEY:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Invalid or missing API key"},
        )
    response = await call_next(request)
    return response


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(product_router.router)
app.include_router(cart_router.router)
app.include_router(order_router.router)
app.include_router(root_router.router)

celery = Celery(
    __name__,
    broker=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_DB}",
    backend=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_DB}"
)
celery.conf.imports = [
    'ecommerce.orders.tasks',
]

if "__main__" == __name__:
    uvicorn.run(app=app)
