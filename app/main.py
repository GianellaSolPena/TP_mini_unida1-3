from fastapi import FastAPI

from app.pedido.routers import router as pedido_router
from app.producto.routers import (
    ErrorDominio,
    manejar_error_dominio,
    router as producto_router,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="API- TP mini",
        description="Aplicacion de unidad 1 - unidad 3",
        version="1.0.0",
    )
    app.add_exception_handler(ErrorDominio, manejar_error_dominio)
    app.include_router(producto_router)
    app.include_router(pedido_router)
    return app


app = create_app()