from .app.pedido.schemas import PedidoRead


class cliente:
    pedidos: list[PedidoRead] = []
