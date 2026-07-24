from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route


async def health(request: Request) -> Response:
    return JSONResponse({"status": "ok"})


def get_routes() -> [Route]:
    return [
        Route("/health", endpoint=health, methods=["GET"]),
    ]
