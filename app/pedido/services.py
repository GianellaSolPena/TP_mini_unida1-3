import asyncio
import time

from app.cliente.cliente import existe_cliente
from app.errores import (
    ClienteNoEncontrado,
    ErrorDominio,
    ProductoNoEncontrado,
    StockInsuficiente,
)
from app.producto.repository import ProductoRepositorio

from .repository import PedidoRepositorio
from .schemas import (
    DemoResultado,
    PedidoCreate,
    PedidoPaginado,
    PedidoRead,
    PedidoUpdate,
)

# R12: protege la sección "leer stock -> restar stock" entre pedidos
# concurrentes. Es un solo lock para toda la app (un solo proceso).
_stock_lock = asyncio.Lock()


async def _verificar_cliente(cliente_id: int) -> None:
    if not await existe_cliente(cliente_id):
        raise ClienteNoEncontrado(f"El cliente {cliente_id} no existe")


async def _verificar_stock(
    producto_repo: ProductoRepositorio, producto_id: int, cantidad: int
) -> None:
    """Chequeo previo (optimista) del stock, con I/O simulada."""
    await asyncio.sleep(0.5)
    producto = producto_repo.buscar_por_id(producto_id)
    if producto is None:
        raise ProductoNoEncontrado(f"El producto {producto_id} no existe")
    disponible = producto.stock - producto.stock_reservado
    if cantidad > disponible:
        raise StockInsuficiente(
            f"Stock insuficiente: piden {cantidad}, disponible {disponible}"
        )


async def crear(
    repo: PedidoRepositorio, producto_repo: ProductoRepositorio, data: PedidoCreate
) -> PedidoRead:
    # R11: cliente y stock se verifican en paralelo; ninguna depende de la otra.
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(_verificar_cliente(data.cliente_id))
            tg.create_task(
                _verificar_stock(producto_repo, data.producto_id, data.cantidad)
            )
    except BaseExceptionGroup as eg:
        # TaskGroup envuelve los errores en un ExceptionGroup: sacamos el
        # error de dominio para responder con el formato propio (R9).
        for exc in eg.exceptions:
            if isinstance(exc, ErrorDominio):
                raise exc from None
        raise

    # R12: entre la verificación de arriba y este punto pudo entrar otro
    # pedido del mismo producto. Por eso se vuelve a leer y se resta
    # adentro del lock: nadie más puede leer/escribir el stock mientras tanto.
    async with _stock_lock:
        producto = producto_repo.buscar_por_id(data.producto_id)
        if producto is None:
            raise ProductoNoEncontrado(f"El producto {data.producto_id} no existe")
        disponible = producto.stock - producto.stock_reservado
        if data.cantidad > disponible:
            raise StockInsuficiente(
                f"Stock insuficiente: piden {data.cantidad}, disponible {disponible}"
            )
        # Simula la escritura en un almacenamiento externo. Este await es el
        # punto donde, SIN el lock, otro pedido podría leer el stock viejo y
        # los dos restarían sobre el mismo valor (condición de carrera).
        await asyncio.sleep(0.05)
        producto.stock = producto.stock - data.cantidad

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


async def demo_secuencial() -> DemoResultado:
    inicio = time.perf_counter()
    resultados = []
    for i in range(3):
        resultados.append(await _verificacion_unitaria(i))
    segundos = time.perf_counter() - inicio
    return DemoResultado(modo="secuencial", resultados=resultados, segundos=round(segundos, 3))


async def demo_concurrente() -> DemoResultado:
    inicio = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        tareas = [tg.create_task(_verificacion_unitaria(i)) for i in range(3)]
    resultados = [t.result() for t in tareas]
    segundos = time.perf_counter() - inicio
    return DemoResultado(modo="concurrente", resultados=resultados, segundos=round(segundos, 3))
