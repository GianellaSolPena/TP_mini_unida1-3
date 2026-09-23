from decimal import Decimal

from typing import Annotated

from pydantic import BaseModel, Field, model_validator


class ProductoBase(BaseModel):
    nombre: Annotated[str, Field(min_length=3)]
    precio: Annotated[Decimal, Field(gt=0)]
    stock: Annotated[int, Field(ge=0)]
    stock_reservado: Annotated[int, Field(ge=0)] = 0
    categoria: str | None = None

    @model_validator(mode="after")
    def validar_relacion_stocks(self) -> "ProductoBase":
        if self.stock_reservado > self.stock:
            raise ValueError(
                "El stock reservado no puede superar al stock total"
            )
        return self


class ProductoCreate(ProductoBase):
    pass


class ProductoRead(ProductoBase):
    id: int


class ProductoUpdate(BaseModel):
    nombre: Annotated[str | None, Field(default=None, min_length=3)]
    precio: Annotated[Decimal | None, Field(default=None, gt=0)]
    stock: Annotated[int | None, Field(default=None, ge=0)]
    stock_reservado: Annotated[int | None, Field(default=None, ge=0)]
    categoria: str | None = None


class ProductoPaginado(BaseModel):
    total: int
    items: list[ProductoRead]