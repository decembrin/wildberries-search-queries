from typing import Any, Callable, List, Optional

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from . import dependencies
from .routers import command_router, search_query_router


def create_app(callbacks: Optional[List[Callable[..., Any]]] = None) -> FastAPI:
    from containers import Container

    container = Container()
    container.wire(
        modules=[
            dependencies,
        ],
    )

    app = FastAPI()
    app.container = container

    app.include_router(command_router.router, prefix='/api/commands')
    app.include_router(search_query_router.router, prefix='/api/queries')

    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=['*'],
        allow_methods=['*'],
        allow_headers=['*'],
    )

    for func in callbacks or []:
        func()

    return app
