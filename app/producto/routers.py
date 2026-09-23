from fastapi import APIRouter, Depends, Path, Query, Request, status
from fastapi.responses import JSONResponse

from . import schemas, services
from .repository import ProductoRepositorio


class ErrorDominio(Exception):
    code = "ERROR_DOMINIO"
    status_code = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ProductoNoEncontrado(ErrorDominio):
    code = "PRODUCTO_NO_ENCONTRADO"
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


router = APIRouter(prefix="/productos", tags=["Productos"])


def get_producto_repo() -> ProductoRepositorio:
    return services.repositorio


@router.get("/", response_model=schemas.ProductoPaginado, status_code=status.HTTP_200_OK)
async def get_productos(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    repo: ProductoRepositorio = Depends(get_producto_repo),
):
    return await services.obtener_todo(repo, offset, limit)


@router.post("/", response_model=schemas.ProductoRead, status_code=status.HTTP_201_CREATED)
async def create_producto(
    producto: schemas.ProductoCreate,
    repo: ProductoRepositorio = Depends(get_producto_repo),
):
    return await services.crear(repo, producto)


@router.get("/{id}", response_model=schemas.ProductoRead, status_code=status.HTTP_200_OK)
async def get_producto_by_id(
    id: int = Path(..., gt=0),
    repo: ProductoRepositorio = Depends(get_producto_repo),
):
    producto = await services.obtener_por_id(repo, id)
    if producto is None:
        raise ProductoNoEncontrado(f"El producto {id} no existe")
    return producto


@router.patch("/{id}", response_model=schemas.ProductoRead, status_code=status.HTTP_200_OK)
async def update_producto(
    producto: schemas.ProductoUpdate,
    id: int = Path(..., gt=0),
    repo: ProductoRepositorio = Depends(get_producto_repo),
):
    actual = await services.obtener_por_id(repo, id)
    if actual is None:
        raise ProductoNoEncontrado(f"El producto {id} no existe")
    for campo in producto.model_fields_set:
        if getattr(producto, campo) is None and campo != "categoria":
            raise AtributoInvalido(f"El campo '{campo}' no admite null")
    actualizado = await services.actualizar(repo, id, producto)
    if actualizado is None:
        raise StockInsuficiente(
            "stock_reservado supera al stock total luego del cambio"
        )
    return actualizado