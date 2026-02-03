from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import schemas, database, models, crud
from ..routers.auth import get_current_active_paid_user

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
    dependencies=[Depends(get_current_active_paid_user)]
)

@router.post("/", response_model=schemas.ProductResponse)
async def create_product(product: schemas.ProductCreate, current_user: models.User = Depends(get_current_active_paid_user), db: AsyncSession = Depends(database.get_db)):
    return await crud.create_product(db=db, product=product, user_id=current_user.id)

@router.get("/", response_model=List[schemas.ProductResponse])
async def read_products(current_user: models.User = Depends(get_current_active_paid_user), db: AsyncSession = Depends(database.get_db)):
    return await crud.get_products(db=db, user_id=current_user.id)

@router.put("/{product_id}", response_model=schemas.ProductResponse)
async def update_product(product_id: int, product: schemas.ProductCreate, current_user: models.User = Depends(get_current_active_paid_user), db: AsyncSession = Depends(database.get_db)):
    db_product = await crud.update_product(db=db, product_id=product_id, product_update=product, user_id=current_user.id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found or not owned by user")
    return db_product

@router.delete("/{product_id}")
async def delete_product(product_id: int, current_user: models.User = Depends(get_current_active_paid_user), db: AsyncSession = Depends(database.get_db)):
    success = await crud.delete_product(db=db, product_id=product_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found or not owned by user")
    return {"message": "Product deleted successfully"}
