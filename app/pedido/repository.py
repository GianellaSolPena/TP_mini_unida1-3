from .schemas import PedidoCreate, PedidoRead, PedidoUpdate


class PedidoRepositorio:
    def __init__(self) -> None:
        self.db: list[PedidoRead] = [
            PedidoRead(
                id=1,
                producto_id=1,
                cliente_id=101,
                cantidad=2,
                estado="confirmado",
            ),
            PedidoRead(
                id=2,
                producto_id=2,
                cliente_id=102,
                cantidad=1,
                estado="confirmado",
            ),
        ]
        self.id_counter: int = max((p.id for p in self.db), default=0) + 1

    def buscar_por_id(self, id: int) -> PedidoRead | None:
        for p in self.db:
            if p.id == id:
                return p
        return None

    def listar(self) -> list[PedidoRead]:
        return self.db

    def crear(self, data: PedidoCreate) -> PedidoRead:
        # El servidor asigna id y fuerza estado "confirmado".
        pedido = PedidoRead(
            id=self.id_counter,
            producto_id=data.producto_id,
            cliente_id=data.cliente_id,
            cantidad=data.cantidad,
            estado="confirmado",
        )
        self.id_counter += 1
        self.db.append(pedido)
        return pedido

    def modificar(self, id: int, data: PedidoUpdate) -> PedidoRead | None:
        for i, p in enumerate(self.db):
            if p.id == id:
                cambios = {
                    campo: getattr(data, campo) for campo in data.model_fields_set
                }
                actualizado = p.model_copy(update=cambios)
                self.db[i] = actualizado
                return actualizado
        return None
