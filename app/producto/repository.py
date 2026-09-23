from decimal import Decimal

from .schemas import ProductoCreate, ProductoRead, ProductoUpdate


class ProductoRepositorio:
    def __init__(self) -> None:
        self.db: list[ProductoRead] = [
            ProductoRead(
                id=1,
                nombre="Teclado mecanico",
                precio=Decimal("15000.00"),
                stock=10,
                stock_reservado=2,
                categoria="perifericos",
            ),
            ProductoRead(
                id=2,
                nombre="Mouse inalambrico",
                precio=Decimal("8500.50"),
                stock=5,
                stock_reservado=0,
                categoria="perifericos",
            ),
        ]
        self.id_counter: int = max((p.id for p in self.db), default=0) + 1

    def buscar_por_id(self, id: int) -> ProductoRead | None:
        for p in self.db:
            if p.id == id:
                return p
        return None

    def listar(self) -> list[ProductoRead]:
        return self.db

    def crear(self, data: ProductoCreate) -> ProductoRead:
        producto = ProductoRead(id=self.id_counter, **data.model_dump())
        self.id_counter += 1
        self.db.append(producto)
        return producto

    def modificar(self, id: int, data: ProductoUpdate) -> ProductoRead | None:
        for i, p in enumerate(self.db):
            if p.id == id:
                cambios = {campo: getattr(data, campo) for campo in data.model_fields_set}
                actualizado = p.model_copy(update=cambios)
                if actualizado.stock_reservado > actualizado.stock:
                    return None
                self.db[i] = actualizado
                return actualizado
        return None