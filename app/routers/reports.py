from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from .. import database, models
from ..routers.auth import get_current_active_paid_user

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(get_current_active_paid_user)]
)

@router.get("/pnl")
async def get_profit_and_loss(current_user: models.User = Depends(get_current_active_paid_user), db: AsyncSession = Depends(database.get_db)):
    # Calculate Revenue
    stmt = select(func.sum(models.Sale.total_amount)).where(models.Sale.user_id == current_user.id)
    result = await db.execute(stmt)
    revenue = result.scalar() or 0.0
    
    # Calculate Cost (Requires Join since we didn't snapshot total_cost in new schema)
    # SUM(sale.quantity_sold * product.cost_price)
    stmt_cost = select(func.sum(models.Sale.quantity_sold * models.Product.cost_price))\
        .join(models.Product)\
        .where(models.Sale.user_id == current_user.id)
        
    result_cost = await db.execute(stmt_cost)
    cost = result_cost.scalar() or 0.0
    
    profit = revenue - cost
    
    return {
        "revenue": revenue,
        "cost": cost,
        "profit": profit,
        "currency": "PKR"
    }

@router.get("/daily")
async def get_daily_pnl(current_user: models.User = Depends(get_current_active_paid_user), db: AsyncSession = Depends(database.get_db)):
    # Group by Date
    # SQLite has func.date()
    stmt = select(
        func.date(models.Sale.date).label("day"),
        func.sum(models.Sale.total_amount).label("revenue"),
        func.sum(models.Sale.quantity_sold * models.Product.cost_price).label("cost")
    ).join(models.Product).where(models.Sale.user_id == current_user.id).group_by(func.date(models.Sale.date))
    
    result = await db.execute(stmt)
    rows = result.all()
    
    report = []
    for row in rows:
        revenue = row.revenue or 0.0
        cost = row.cost or 0.0
        profit = revenue - cost
        report.append({
            "date": row.day,
            "revenue": revenue,
            "cost": cost,
            "profit": profit
        })
        
    return report
