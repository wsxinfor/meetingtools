from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.meeting import CustomerCreate, CustomerOut
from app.services import meeting_service

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=dict)
async def create_customer(data: CustomerCreate, db: AsyncSession = Depends(get_db)) -> dict:
    customer = await meeting_service.create_customer(db, data)
    return {"code": 0, "data": CustomerOut.model_validate(customer).model_dump(), "msg": "ok"}


@router.get("", response_model=dict)
async def list_customers(db: AsyncSession = Depends(get_db)) -> dict:
    customers = await meeting_service.list_customers(db)
    return {
        "code": 0,
        "data": [CustomerOut.model_validate(c).model_dump() for c in customers],
        "msg": "ok",
    }
