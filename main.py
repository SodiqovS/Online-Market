import uvicorn
from celery import Celery
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from ecommerce import config
from ecommerce.auth import router as auth_router

from ecommerce.cart import router as cart_router
from ecommerce.orders import router as order_router
from ecommerce.products import router as product_router
from ecommerce.user import router as user_router
from ecommerce.root import router as root_router


from fastapi_pagination import add_pagination

description = """
Online Market API
## Auth
You will be able to:
* Login or register an account
* Refresh your access token

## Users

You will be able to:

* **Read users**  (admin)
* **Update users** (admin)
* **Delete users** (admin)
* **Profile methods**

## Products

You will be able to:
* **Create categories** (admin)
* **Read categories**
* **Update categories** (admin)
* **Delete categories** (admin)

* **Create products** (admin)
* **Read products**
* **Update products** (admin)
* **Delete products** (admin)

## Cart
You will be able to:
* **Add cart to item**
* ** Remove cart from item**
* **Update cart item quantity**

## Order
You will be able to:
* **Create orders**
* **Ger your orders**
* **Get all orders** (admin)

"""


app = FastAPI(
    title="EcommerceApp",
    description=description,
    version="0.0.3",
    contact={
        "name": "Sodiqov Sodiqjon",
        "email": "sodiqovs2002@gmail.com",
    },
)


add_pagination(app)
origins = ["*"]


app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow only the specific server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Authentication
API_KEY = config.XAPIKEY


# @app.middleware("http")
# async def verify_api_key(request: Request, call_next):
#     api_key = request.cookies.get("x-api-key")
#     if api_key != API_KEY:
#         return JSONResponse(
#             status_code=status.HTTP_403_FORBIDDEN,
#             content={"detail": "Invalid or missing API key"},
#         )
#     response = await call_next(request)
#     return response


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
