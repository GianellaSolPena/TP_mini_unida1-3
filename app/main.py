from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.pedido import services as pedido_services
from app.pedido.repository import PedidoRepositorio
from app.pedido.routers import router as pedido_router
from app.producto import services as producto_services
from app.producto.repository import ProductoRepositorio
from app.producto.routers import (
    ErrorDominio,
    manejar_error_dominio,
    router as producto_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # R4: los recursos compartidos se crean una sola vez acá,
    # no en cada pedido. Los Depends los devuelven desde services.
    app.state.productos = ProductoRepositorio()
    app.state.pedidos = PedidoRepositorio()
    producto_services.repositorio = app.state.productos
    pedido_services.repositorio = app.state.pedidos
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="API- TP mini",
        description="Aplicacion de unidad 1 - unidad 3",
        version="1.0.0",
        lifespan=lifespan,
    )
    # Un solo handler: pedido reusa ErrorDominio de producto (formato único, R9).
    app.add_exception_handler(ErrorDominio, manejar_error_dominio)
    app.include_router(producto_router)
    app.include_router(pedido_router)
    return app


app = create_app()
