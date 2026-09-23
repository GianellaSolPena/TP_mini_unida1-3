from fastapi import APIRouter, BackgroundTasks, Depends, Path, Query, status

from app.producto.repository import ProductoRepositorio
from app.producto.routers import ErrorDominio, get_producto_repo

from . import schemas, services
from .repository import PedidoRepositorio
from .services import ClienteNoEncontrado  # noqa: F401 (re-export para main/tests)


class PedidoNoEncontrado(ErrorDominio):
    code = "PEDIDO_NO_ENCONTRADO"
    status_code = 404


class AtributoInvalido(ErrorDominio):
    code = "ATRIBUTO_INVALIDO"
    status_code = 400


router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


def get_pedido_repo() -> PedidoRepositorio:
    return services.repositorio


def _notificar_pedido_confirmado(pedido_id: int, cliente_id: int) -> None:
    # R13: tarea en segundo plano (la ejecuta FastAPI vía BackgroundTasks).
    # Acá iría el envío real (mail, webhook, etc.); dejamos un log.
    print(f"[notificacion] pedido {pedido_id} confirmado para cliente {cliente_id}")


@router.get("/", response_model=schemas.PedidoPaginado, status_code=status.HTTP_200_OK)
async def get_pedidos(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    repo: PedidoRepositorio = Depends(get_pedido_repo),
):
    return await services.obtener_todo(repo, offset, limit)


# R14: van antes de "/{id}" para que no los capture el path param.
@router.get(
    "/demo/secuencial", response_model=dict, status_code=status.HTTP_200_OK
)
async def demo_secuencial():
    return await services.demo_secuencial()


@router.get(
    "/demo/concurrente", response_model=dict, status_code=status.HTTP_200_OK
)
async def demo_concurrente():
    return await services.demo_concurrente()


@router.post("/", response_model=schemas.PedidoRead, status_code=status.HTTP_201_CREATED)
async def create_pedido(
    pedido: schemas.PedidoCreate,
    background_tasks: BackgroundTasks,
    repo: PedidoRepositorio = Depends(get_pedido_repo),
    producto_repo: ProductoRepositorio = Depends(get_producto_repo),
):
    nuevo = await services.crear(repo, producto_repo, pedido)
    # R13: notificación con la herramienta del framework, no create_task suelto.
    background_tasks.add_task(
        _notificar_pedido_confirmado, nuevo.id, nuevo.cliente_id
    )
    return nuevo


@router.get("/{id}", response_model=schemas.PedidoRead, status_code=status.HTTP_200_OK)
async def get_pedido_by_id(
    id: int = Path(..., gt=0),
    repo: PedidoRepositorio = Depends(get_pedido_repo),
):
    pedido = await services.obtener_por_id(repo, id)
    if pedido is None:
        raise PedidoNoEncontrado(f"El pedido {id} no existe")
    return pedido


@router.patch("/{id}", response_model=schemas.PedidoRead, status_code=status.HTTP_200_OK)
async def update_pedido(
    pedido: schemas.PedidoUpdate,
    id: int = Path(..., gt=0),
    repo: PedidoRepositorio = Depends(get_pedido_repo),
):
    actual = await services.obtener_por_id(repo, id)
    if actual is None:
        raise PedidoNoEncontrado(f"El pedido {id} no existe")
    # En pedido ningún campo admite null explícito (no hay opcional anulable
    # como "categoria" en producto): null siempre es error.
    for campo in pedido.model_fields_set:
        if getattr(pedido, campo) is None:
            raise AtributoInvalido(f"El campo '{campo}' no admite null")
    actualizado = await services.actualizar(repo, id, pedido)
    if actualizado is None:
        raise PedidoNoEncontrado(f"El pedido {id} no existe")
    return actualizado
