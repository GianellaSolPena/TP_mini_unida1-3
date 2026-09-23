"""Evidencia de R11 y R12 bajo concurrencia real.

Uso (con la API corriendo en otra terminal):
    python scripts/pedidos_concurrentes.py
    python scripts/pedidos_concurrentes.py --url http://127.0.0.1:8000 --pedidos 20 --producto 2

Qué demuestra:
  R11 - Un pedido tarda ~0.5 s y no ~1 s: la verificación del cliente
        (0.5 s) y la del stock (0.5 s) corren en paralelo con TaskGroup.
  R12 - Se disparan N pedidos del MISMO producto al mismo tiempo con
        asyncio.gather. Se confirman exactamente tantos como unidades había
        disponibles, el resto recibe 409, y el stock final cierra justo:
        ningún pedido pisó la resta de otro.
"""

import argparse
import asyncio
import time

import httpx


async def pedir(client: httpx.AsyncClient, producto_id: int, i: int):
    inicio = time.perf_counter()
    r = await client.post(
        "/pedidos/",
        json={"producto_id": producto_id, "cliente_id": 101 + (i % 3), "cantidad": 1},
    )
    return r, time.perf_counter() - inicio


async def main(url: str, n: int, producto_id: int) -> None:
    async with httpx.AsyncClient(base_url=url, timeout=30) as client:
        antes = (await client.get(f"/productos/{producto_id}")).json()
        disponible = antes["stock"] - antes["stock_reservado"]
        print(f"Producto {producto_id} ({antes['nombre']}): stock={antes['stock']}, "
              f"reservado={antes['stock_reservado']}, disponible={disponible}")

        # ---- R11: un pedido solo, midiendo el tiempo ----
        print("\n== R11: verificaciones concurrentes ==")
        r, t = await pedir(client, producto_id, 0)
        print(f"1 pedido  -> {r.status_code} en {t:.2f} s "
              "(secuencial serían ~1.0 s: 0.5 cliente + 0.5 stock)")
        r = await client.post("/pedidos/", json={"producto_id": 999, "cliente_id": 999, "cantidad": 1})
        print(f"Cliente y producto inexistentes -> {r.status_code} {r.json()}")
        disponible -= 1

        # ---- R12: N pedidos simultáneos del mismo producto ----
        print(f"\n== R12: {n} pedidos simultáneos de 1 unidad (quedan {disponible}) ==")
        inicio = time.perf_counter()
        resultados = await asyncio.gather(*[pedir(client, producto_id, i) for i in range(n)])
        total = time.perf_counter() - inicio

        ok = [r for r, _ in resultados if r.status_code == 201]
        sin_stock = [r for r, _ in resultados if r.status_code == 409]
        despues = (await client.get(f"/productos/{producto_id}")).json()

        print(f"Confirmados (201): {len(ok)}")
        print(f"Rechazados  (409): {len(sin_stock)}")
        print(f"Otros:             {n - len(ok) - len(sin_stock)}")
        print(f"Tiempo total:      {total:.2f} s")
        print(f"Stock final:       {despues['stock']} (reservado {despues['stock_reservado']})")
        if sin_stock:
            print(f"Ejemplo de rechazo: {sin_stock[0].json()}")

        esperado_ok = min(n, max(disponible, 0))
        stock_esperado = antes["stock"] - 1 - len(ok)
        correcto = len(ok) == esperado_ok and despues["stock"] == stock_esperado \
            and despues["stock"] >= despues["stock_reservado"]
        print("\nRESULTADO:", "OK - no hubo sobreventa ni restas pisadas" if correcto
              else "FALLA - hubo una condición de carrera")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://127.0.0.1:8000")
    p.add_argument("--pedidos", type=int, default=20)
    p.add_argument("--producto", type=int, default=1)
    a = p.parse_args()
    asyncio.run(main(a.url, a.pedidos, a.producto))
