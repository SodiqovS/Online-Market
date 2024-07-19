from fastapi import APIRouter, Request


router = APIRouter(
    tags=['root'],
    prefix=''
)


@router.get("/")
async def root(request: Request):

    return {
        "host": request.client.host,
        "port": request.client.port,
    }
