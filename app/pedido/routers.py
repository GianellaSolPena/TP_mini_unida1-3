from fastapi import APIRouter, Path, Query, status, HTTPException

from . import services

from . import schemas

router = APIRouter(prefix="/pedido", tags=["Pedidos"])
