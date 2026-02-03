from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from . import models, schemas
from .auth import utils

# User CRUD
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = utils.get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password_hash=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# Product CRUD
async def get_products(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.Product).where(models.Product.user_id == user_id))
    return result.scalars().all()

async def create_product(db: AsyncSession, product: schemas.ProductCreate, user_id: int):
    db_product = models.Product(**product.dict(), user_id=user_id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

async def get_product(db: AsyncSession, product_id: int, user_id: int):
    result = await db.execute(select(models.Product).where(models.Product.id == product_id, models.Product.user_id == user_id))
    return result.scalars().first()

async def update_product(db: AsyncSession, product_id: int, product_update: schemas.ProductCreate, user_id: int):
    # Fetch existing
    db_product = await get_product(db, product_id, user_id)
    if not db_product:
        return None
    
    # Update fields
    db_product.name = product_update.name
    db_product.cost_price = product_update.cost_price
    db_product.selling_price = product_update.selling_price
    db_product.stock_quantity = product_update.stock_quantity
    
    await db.commit()
    await db.refresh(db_product)
    return db_product

async def delete_product(db: AsyncSession, product_id: int, user_id: int):
    db_product = await get_product(db, product_id, user_id)
    if not db_product:
        return False
        
    await db.delete(db_product)
    await db.commit()
    return True

# Sale CRUD
async def get_sales(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.Sale).where(models.Sale.user_id == user_id).order_by(models.Sale.date.desc()))
    return result.scalars().all()
async def create_sale(db: AsyncSession, sale: schemas.SaleCreate, user_id: int):
    # Fetch product to get current price and stock
    result = await db.execute(select(models.Product).where(models.Product.id == sale.product_id, models.Product.user_id == user_id))
    product = result.scalars().first()
    
    if not product:
        return None # Product not found or not owned by user
    
    if product.stock_quantity < sale.quantity:
        raise ValueError("Insufficient stock")

    total_amount = product.selling_price * sale.quantity
    
    # We stopped tracking total_cost explicit snapshot in the simplified schema requirement, 
    # but strictly "Calculate profit and loss" usually implies we need it. 
    # The requirement said "Sales: product_id, quantity_sold, date". 
    # It didn't explicitly forbid total_amount/cost, but let's stick to the model we defined 
    # which HAS total_amount but removed total_cost snapshot (unless I should iterate).
    # Wait, my models.py still has `total_amount`. 
    # I should better snapshot cost too if I want accurate P&L later, but user didn't ask for it in "Sales" table reqs.
    # However, for P&L I need cost. I will calculate P&L dynamically from Product link or re-add it? 
    # The user said "Requirements: ... Explain briefly why each table exists".
    # In my plan I wrote: "Snapshots price...".
    # I will stick to the plan which had `total_amount`. 
    
    db_sale = models.Sale(
        user_id=user_id,
        product_id=sale.product_id,
        quantity_sold=sale.quantity,
        total_amount=total_amount
    )
    
    # Update stock
    product.stock_quantity -= sale.quantity
    
    db.add(db_sale)
    await db.commit()
    await db.refresh(db_sale)
    return db_sale
