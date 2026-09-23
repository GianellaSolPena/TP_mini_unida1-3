"""Errores del dominio y su handler (R9).

Todos los errores de negocio heredan de ErrorDominio y se responden con
el mismo formato estable:

    {"error": {"code": "...", "message": "..."}}
"""

from fastapi import Request
from fastapi.responses import JSONResponse


class ErrorDominio(Exception):
    code = "ERROR_DOMINIO"
    status_code = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ProductoNoEncontrado(ErrorDominio):
    code = "PRODUCTO_NO_ENCONTRADO"
    status_code = 404


class PedidoNoEncontrado(ErrorDominio):
    code = "PEDIDO_NO_ENCONTRADO"
    status_code = 404


class ClienteNoEncontrado(ErrorDominio):
    code = "CLIENTE_NO_ENCONTRADO"
    status_code = 404


class StockInsuficiente(ErrorDominio):
    code = "STOCK_INSUFICIENTE"
    status_code = 409


class AtributoInvalido(ErrorDominio):
    code = "ATRIBUTO_INVALIDO"
    status_code = 400


async def manejar_error_dominio(request: Request, exc: ErrorDominio) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )
