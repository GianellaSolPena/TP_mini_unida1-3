"""Clientes ya registrados del kiosco (consigna §2: ids fijos, sin alta)."""

CLIENTES_REGISTRADOS: set[int] = {101, 102, 103}


def existe_cliente(cliente_id: int) -> bool:
    return cliente_id in CLIENTES_REGISTRADOS
