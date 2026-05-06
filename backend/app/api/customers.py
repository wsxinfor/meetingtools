import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.meeting import Customer, Project
from app.schemas.meeting import CustomerCreate, CustomerOut, CustomerUpdate
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


@router.get("/{customer_id}", response_model=dict)
async def get_customer(customer_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict:
    customer = await meeting_service.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    return {"code": 0, "data": CustomerOut.model_validate(customer).model_dump(), "msg": "ok"}


@router.put("/{customer_id}", response_model=dict)
async def update_customer(
    customer_id: uuid.UUID, data: CustomerUpdate, db: AsyncSession = Depends(get_db)
) -> dict:
    customer = await meeting_service.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    customer = await meeting_service.update_customer(db, customer, data)
    return {"code": 0, "data": CustomerOut.model_validate(customer).model_dump(), "msg": "ok"}


@router.delete("/{customer_id}", response_model=dict)
async def delete_customer(customer_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict:
    customer = await meeting_service.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    count = (
        await db.execute(select(func.count()).select_from(Project).where(Project.customer_id == customer_id))
    ).scalar_one()
    if count > 0:
        raise HTTPException(status_code=400, detail="该客户下存在项目，无法删除")
    await meeting_service.delete_customer(db, customer)
    return {"code": 0, "data": None, "msg": "ok"}
