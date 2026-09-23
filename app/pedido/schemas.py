from pydantic import BaseModel, Field

from typing import Optional, Annotated

from enum import Enum


class EstadoPedido(str, Enum):
    CONFIRMADO = "confirmado"
    CANCELADO = "cancelado"


class PedidoBase(BaseModel):
    cantidad: Annotated[int, Field(gt=0)]
    estado: EstadoPedido.CONFIRMADO


class PedidoCreate(PedidoBase):
    pass


class PedidoRead(PedidoBase):
    id: int


class PedidoUpdate(BaseModel):
    pass
