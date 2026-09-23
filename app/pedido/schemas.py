from typing import Annotated

from pydantic import BaseModel, Field


class PedidoCreate(BaseModel):
    """Lo que envía el cliente. El id y el estado los asigna el servidor."""

    producto_id: Annotated[int, Field(gt=0)]
    cliente_id: Annotated[int, Field(gt=0)]
    cantidad: Annotated[int, Field(gt=0)]


class PedidoRead(BaseModel):
    """Lo que devuelve la API. Estado siempre 'confirmado' al crearse."""

    id: int
    producto_id: int
    cliente_id: int
    cantidad: Annotated[int, Field(gt=0)]
    estado: str = "confirmado"


class PedidoUpdate(BaseModel):
    """PATCH de pedido: solo se puede ajustar la cantidad.

    No incluye id / producto_id / cliente_id (no se cambian) ni
    estado (lo fija el servidor). Ningún campo admite null explícito.
    """

    cantidad: Annotated[int | None, Field(default=None, gt=0)] = None


class PedidoPaginado(BaseModel):
    total: int
    items: list[PedidoRead]


class DemoResultado(BaseModel):
    """Respuesta de /pedidos/demo/* (R14): así /docs muestra el esquema real."""

    modo: str
    resultados: list[int]
    segundos: float
