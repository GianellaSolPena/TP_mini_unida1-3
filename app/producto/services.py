import asyncio

from .repository import ProductoRepositorio
from .schemas import ProductoCreate, ProductoPaginado, ProductoRead, ProductoUpdate

repositorio = ProductoRepositorio()


async def crear(repo: ProductoRepositorio, data: ProductoCreate) -> ProductoRead:
    await asyncio.sleep(2)
    return repo.crear(data)


async def obtener_todo(
    repo: ProductoRepositorio, offset: int = 0, limit: int = 10
) -> ProductoPaginado:
    await asyncio.sleep(4)
    todos = repo.listar()
    return ProductoPaginado(total=len(todos), items=todos[offset : offset + limit])


async def obtener_por_id(repo: ProductoRepositorio, id: int) -> ProductoRead | None:
    await asyncio.sleep(2)
    return repo.buscar_por_id(id)


async def actualizar(
    repo: ProductoRepositorio, id: int, data: ProductoUpdate
) -> ProductoRead | None:
    await asyncio.sleep(2)
    return repo.modificar(id, data)