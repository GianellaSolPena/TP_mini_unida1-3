from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.errores import ErrorDominio, manejar_error_dominio
from app.pedido.repository import PedidoRepositorio
from app.pedido.routers import router as pedido_router
from app.producto.repository import ProductoRepositorio
from app.producto.routers import router as producto_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # R4: los recursos compartidos se crean una sola vez acá, al arrancar,
    # y se guardan en app.state. Los Depends (app/dependencias.py) los leen
    # desde request.app.state en cada pedido.
    app.state.productos = ProductoRepositorio()
    app.state.pedidos = PedidoRepositorio()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="API - TP mini",
        description="Kiosco: catálogo y pedidos (unidades 1 a 3)",
        version="1.0.0",
        lifespan=lifespan,
    )
    # R9: un solo handler para todos los errores del dominio.
    app.add_exception_handler(ErrorDominio, manejar_error_dominio)
    app.include_router(producto_router)
    app.include_router(pedido_router)
    return app


app = create_app()
