import asyncio

from .repository import ProductoRepositorio
from .schemas import ProductoCreate, ProductoPaginado, ProductoRead, ProductoUpdate

# Latencia simulada de I/O (como si el repositorio fuera remoto).
# Es corta a propósito: no debe hacer lenta la API.
LATENCIA_IO = 0.1


async def crear(repo: ProductoRepositorio, data: ProductoCreate) -> ProductoRead:
    await asyncio.sleep(LATENCIA_IO)
    return repo.crear(data)


async def obtener_todo(
    repo: ProductoRepositorio, offset: int = 0, limit: int = 10
) -> ProductoPaginado:
    await asyncio.sleep(LATENCIA_IO)
    todos = repo.listar()
    return ProductoPaginado(total=len(todos), items=todos[offset : offset + limit])


async def obtener_por_id(repo: ProductoRepositorio, id: int) -> ProductoRead | None:
    await asyncio.sleep(LATENCIA_IO)
    return repo.buscar_por_id(id)


async def actualizar(
    repo: ProductoRepositorio, id: int, data: ProductoUpdate
) -> ProductoRead | None:
    await asyncio.sleep(LATENCIA_IO)
    return repo.modificar(id, data)
