from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from .. import schemas, database, models, crud
from ..routers.auth import get_current_active_paid_user

router = APIRouter(
    prefix="/sales",
    tags=["Sales"],
    dependencies=[Depends(get_current_active_paid_user)]
)

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.post("/", response_model=schemas.SaleResponse)
async def create_sale(sale: schemas.SaleCreate, current_user: models.User = Depends(get_current_active_paid_user), db: AsyncSession = Depends(database.get_db)):
    try:
        db_sale = await crud.create_sale(db=db, sale=sale, user_id=current_user.id)
        if db_sale is None:
             raise HTTPException(status_code=404, detail="Product not found or not owned by user")
        
        # Explicit fetch for response
        product_stmt = await db.execute(select(models.Product).where(models.Product.id == sale.product_id))
        product = product_stmt.scalars().first()
        
        return schemas.SaleResponse(
            id=db_sale.id,
            product_name=product.name if product else "Unknown",
            quantity_sold=db_sale.quantity_sold,
            total_amount=db_sale.total_amount,
            date=db_sale.date
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.SaleResponse])
async def read_sales(current_user: models.User = Depends(get_current_active_paid_user), db: AsyncSession = Depends(database.get_db)):
    try:
        sales = await crud.get_sales(db=db, user_id=current_user.id)
        
        # Explicitly fetch products via a second query to avoid async relationship loading issues
        product_ids = [s.product_id for s in sales]
        start_products = {}
        if product_ids:
            stmt = select(models.Product).where(models.Product.id.in_(product_ids))
            result = await db.execute(stmt)
            products = result.scalars().all()
            start_products = {p.id: p for p in products}

        response = []
        for sale in sales:
            product = start_products.get(sale.product_id)
            response.append(schemas.SaleResponse(
                id=sale.id,
                product_name=product.name if product else "Unknown",
                quantity_sold=sale.quantity_sold,
                total_amount=sale.total_amount,
                date=sale.date
            ))
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
