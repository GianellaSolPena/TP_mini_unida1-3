# Mini TP — Kiosco: catálogo y pedidos

Integrador de los capítulos 1 a 3 · Programación III · TUP, UTN FRM.

API hecha con **FastAPI** para un kiosco que tiene un catálogo de productos y recibe pedidos de clientes ya registrados (ids 101, 102 y 103). Todo se guarda en memoria, sin base de datos.

## Requisitos

- Python 3.11 o superior (se usa `asyncio.TaskGroup`)

## Cómo correrlo

```bash
# 1. Crear y activar un entorno virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Levantar la API (desde la carpeta raíz del proyecto)
fastapi dev app/main.py
# o también:  uvicorn app.main:app --reload
```

La API queda en `http://127.0.0.1:8000` y la documentación interactiva en **http://127.0.0.1:8000/docs**.

## Endpoints

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/productos/?offset=0&limit=10` | Lista paginada, incluye `total` |
| POST | `/productos/` | Crea un producto |
| GET | `/productos/{id}` | Busca un producto |
| PATCH | `/productos/{id}` | Actualización parcial (un campo omitido no se toca; `categoria: null` la borra) |
| GET | `/pedidos/?offset=0&limit=10` | Lista paginada de pedidos |
| POST | `/pedidos/` | Crea un pedido (`producto_id`, `cliente_id`, `cantidad`) |
| GET | `/pedidos/{id}` | Busca un pedido |
| PATCH | `/pedidos/{id}` | Modifica la cantidad |
| GET | `/pedidos/demo/secuencial` | 3 verificaciones una atrás de otra (~1.5 s) |
| GET | `/pedidos/demo/concurrente` | Las mismas 3 en paralelo (~0.5 s) |

Los errores del dominio responden siempre con este formato:

```json
{"error": {"code": "STOCK_INSUFICIENTE", "message": "Stock insuficiente: piden 5, disponible 2"}}
```

Los códigos posibles son `PRODUCTO_NO_ENCONTRADO`, `PEDIDO_NO_ENCONTRADO`, `CLIENTE_NO_ENCONTRADO` (404), `STOCK_INSUFICIENTE` (409) y `ATRIBUTO_INVALIDO` (400).

## Evidencia de concurrencia (R11 y R12)

Con la API corriendo, abrí otra terminal (con el entorno virtual activado) y ejecutá:

```bash
python scripts/pedidos_concurrentes.py
```

El script dispara 20 pedidos del mismo producto **al mismo tiempo** con `asyncio.gather` y muestra:

- **R11**: un pedido tarda ~0.5 s y no ~1 s, porque la verificación del cliente y la del stock corren en paralelo.
- **R12**: se confirman exactamente tantos pedidos como unidades había disponibles, el resto recibe 409 y el stock final da justo.

La salida de una corrida está guardada en [`evidencia/concurrencia.log`](evidencia/concurrencia.log).

> Para comparar: si se saca el `async with _stock_lock` de `app/pedido/services.py`, con 8 unidades disponibles se confirman los 20 pedidos y el stock queda negativo. Eso es la condición de carrera que el lock evita.

## Estructura

```
app/
├── main.py            # create_app + lifespan (crea los repositorios una sola vez)
├── dependencias.py    # Depends que entregan los repositorios desde app.state
├── errores.py         # errores del dominio + handler con formato propio
├── cliente/           # clientes registrados (ids fijos)
├── producto/          # schemas · repository · services · routers
└── pedido/            # schemas · repository · services · routers
scripts/
└── pedidos_concurrentes.py
evidencia/
└── concurrencia.log
```

## Dónde se cumple cada requisito

| Req. | Dónde |
|---|---|
| R1 | Todos los handlers en `*/routers.py` son `async def` |
| R2 | `app/dependencias.py` → `Depends(get_producto_repo)` / `Depends(get_pedido_repo)` |
| R3 | `response_model` en cada endpoint (las demos usan `DemoResultado`) |
| R4 | `lifespan` en `app/main.py` |
| R5 | `ProductoCreate`, `ProductoUpdate`, `ProductoRead` en `app/producto/schemas.py` |
| R6 | `precio: Decimal` con `Field(gt=0)` |
| R7 | `Field(ge=0)` por campo + `@model_validator` para `stock_reservado <= stock` |
| R8 | `ProductoPaginado(total, items)` |
| R9 | `app/errores.py` + `add_exception_handler` en `main.py` |
| R10 | `model_fields_set` en el PATCH de producto |
| R11 | `asyncio.TaskGroup` en `app/pedido/services.py::crear` |
| R12 | `asyncio.Lock` alrededor de la resta de stock |
| R13 | `BackgroundTasks` en `POST /pedidos/` |
| R14 | `/pedidos/demo/secuencial` y `/pedidos/demo/concurrente` |
