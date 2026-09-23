import asyncio
import time

from app.producto.repository import ProductoRepositorio
from app.producto.routers import (
    ErrorDominio,
    ProductoNoEncontrado,
    StockInsuficiente,
)

from .repository import PedidoRepositorio
from .schemas import PedidoCreate, PedidoPaginado, PedidoRead, PedidoUpdate

repositorio = PedidoRepositorio()

CLIENTES_REGISTRADOS: set[int] = {101, 102, 103}

# R12: protege la resta de stock entre pedidos concurrentes.
_stock_lock = asyncio.Lock()


class ClienteNoEncontrado(ErrorDominio):
    code = "CLIENTE_NO_ENCONTRADO"
    status_code = 404


async def _verificar_cliente(cliente_id: int) -> None:
    """Simula una verificación I/O (p.ej. consulta a otro servicio)."""
    await asyncio.sleep(0.5)
    if cliente_id not in CLIENTES_REGISTRADOS:
        raise ClienteNoEncontrado(f"El cliente {cliente_id} no existe")


async def _verificar_stock(
    producto_repo: ProductoRepositorio, producto_id: int, cantidad: int
):
    """Simula una verificación I/O y devuelve el producto."""
    await asyncio.sleep(0.5)
    producto = producto_repo.buscar_por_id(producto_id)
    if producto is None:
        raise ProductoNoEncontrado(f"El producto {producto_id} no existe")
    disponible = producto.stock - producto.stock_reservado
    if cantidad > disponible:
        raise StockInsuficiente(
            f"Stock insuficiente: piden {cantidad}, disponible {disponible}"
        )
    return producto


async def crear(
    repo: PedidoRepositorio, producto_repo: ProductoRepositorio, data: PedidoCreate
) -> PedidoRead:
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(_verificar_cliente(data.cliente_id))
            tg.create_task(
                _verificar_stock(producto_repo, data.producto_id, data.cantidad)
            )
    except BaseExceptionGroup as eg:
        # TaskGroup envuelve en ExceptionGroup: desempaquetamos para
        # conservar el formato propio de errores del dominio (R9).
        for exc in eg.exceptions:
            if isinstance(exc, ErrorDominio):
                raise exc
        raise

    
    async with _stock_lock:
        producto = producto_repo.buscar_por_id(data.producto_id)
        if producto is None:
            raise ProductoNoEncontrado(f"El producto {data.producto_id} no existe")
        disponible = producto.stock - producto.stock_reservado
        if data.cantidad > disponible:
            raise StockInsuficiente(
                f"Stock insuficiente: piden {data.cantidad}, disponible {disponible}"
            )
        producto.stock -= data.cantidad

    return repo.crear(data)


async def obtener_todo(
    repo: PedidoRepositorio, offset: int = 0, limit: int = 10
) -> PedidoPaginado:
    await asyncio.sleep(0.1)
    todos = repo.listar()
    return PedidoPaginado(total=len(todos), items=todos[offset : offset + limit])


async def obtener_por_id(repo: PedidoRepositorio, id: int) -> PedidoRead | None:
    await asyncio.sleep(0.1)
    return repo.buscar_por_id(id)


async def actualizar(
    repo: PedidoRepositorio, id: int, data: PedidoUpdate
) -> PedidoRead | None:
    await asyncio.sleep(0.1)
    return repo.modificar(id, data)


# ---- R14: demo secuencial vs concurrente con tiempos reales ----
async def _verificacion_unitaria(n: int) -> int:
    await asyncio.sleep(0.5)
    return n


async def demo_secuencial() -> dict:
    inicio = time.perf_counter()
    resultados = []
    for i in range(3):
        resultados.append(await _verificacion_unitaria(i))
    fin = time.perf_counter()
    return {"modo": "secuencial", "resultados": resultados, "segundos": round(fin - inicio, 3)}


async def demo_concurrente() -> dict:
    inicio = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        tareas = [tg.create_task(_verificacion_unitaria(i)) for i in range(3)]
    resultados = [t.result() for t in tareas]
    fin = time.perf_counter()
    return {"modo": "concurrente", "resultados": resultados, "segundos": round(fin - inicio, 3)}
