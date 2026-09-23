"""Dependencias compartidas (R2).

Los repositorios se crean UNA sola vez en el lifespan (R4) y se guardan
en app.state. Estas funciones los entregan a cada handler vía Depends(),
sin variables globales sueltas.
"""

from fastapi import Request

from app.pedido.repository import PedidoRepositorio
from app.producto.repository import ProductoRepositorio


def get_producto_repo(request: Request) -> ProductoRepositorio:
    return request.app.state.productos


def get_pedido_repo(request: Request) -> PedidoRepositorio:
    return request.app.state.pedidos
