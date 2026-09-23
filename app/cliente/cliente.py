"""Clientes ya registrados del kiosco (consigna §2: ids fijos, sin alta)."""

import asyncio

CLIENTES_REGISTRADOS: frozenset[int] = frozenset({101, 102, 103})


async def existe_cliente(cliente_id: int) -> bool:
    """Simula una consulta I/O (p. ej. a un servicio de clientes)."""
    await asyncio.sleep(0.5)
    return cliente_id in CLIENTES_REGISTRADOS
