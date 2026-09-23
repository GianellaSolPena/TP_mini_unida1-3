from fastapi import APIRouter, Depends, Path, Query, status

from app.dependencias import get_producto_repo
from app.errores import AtributoInvalido, ProductoNoEncontrado

from . import schemas, services
from .repository import ProductoRepositorio

router = APIRouter(prefix="/productos", tags=["Productos"])


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
    # R10: solo miramos los campos que el cliente ENVIÓ (model_fields_set).
    # "categoria" es el único campo que admite null explícito (lo borra);
    # para el resto, un null enviado es un error.
    for campo in producto.model_fields_set:
        if getattr(producto, campo) is None and campo != "categoria":
            raise AtributoInvalido(f"El campo '{campo}' no admite null")
    # Si el cambio deja stock_reservado > stock, el repositorio levanta
    # AtributoInvalido (dato inválido, no falta de stock).
    return await services.actualizar(repo, id, producto)
