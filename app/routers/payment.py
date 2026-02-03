from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
import hmac
import hashlib
from .. import schemas, database, models, crud
from ..auth import utils
from ..routers.auth import get_current_user

router = APIRouter(
    prefix="/payment",
    tags=["Payment"]
)

JC_MERCHANT_ID = "MC_12345"
JC_PASSWORD = "password_123"
JC_INTEGRITY_SALT = "salt_123"
JC_RETURN_URL = "http://localhost:8000/payment/callback"

def generate_secure_hash(params: dict, salt: str):
    sorted_params = sorted([(k, v) for k, v in params.items() if v != "" and k != "pp_SecureHash"])
    raw_string = salt
    for key, value in sorted_params:
        if value:
            raw_string += f"&{value}"     
    return hmac.new(salt.encode(), raw_string.encode(), hashlib.sha256).hexdigest().upper()

@router.post("/initiate")
async def initiate_payment(payment_request: schemas.PaymentInitiate, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(database.get_db)):
    txn_ref = f"T{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{current_user.id}"
    
    # Create Payment Record (renamed from Transaction)
    payment = models.Payment(
        user_id=current_user.id,
        transaction_id=txn_ref,
        amount=payment_request.amount,
        status="pending"
    )
    db.add(payment)
    await db.commit()
    
    amount_str = f"{payment_request.amount:.2f}"
    params = {
        "pp_Version": "2.0",
        "pp_TxnType": "MWALLET",
        "pp_Language": "EN",
        "pp_MerchantID": JC_MERCHANT_ID,
        "pp_SubMerchantID": "",
        "pp_Password": JC_PASSWORD,
        "pp_BankID": "TBANK",
        "pp_ProductID": "RETAIL",
        "pp_TxnRefNo": txn_ref,
        "pp_Amount": amount_str,
        "pp_TxnCurrency": "PKR",
        "pp_TxnDateTime": datetime.utcnow().strftime("%Y%m%d%H%M%S"),
        "pp_BillReference": "billRef",
        "pp_Description": "Shop Fees",
        "pp_TxnExpiryDateTime": (datetime.utcnow() + utils.timedelta(hours=1)).strftime("%Y%m%d%H%M%S"),
        "pp_ReturnURL": JC_RETURN_URL,
        "pp_SecureHash": "",
        "pp_mpf_1": "1",
        "pp_mpf_2": "2",
        "pp_mpf_3": "3",
        "pp_mpf_4": "4",
        "pp_mpf_5": "5",
    }
    
    secure_hash = generate_secure_hash(params, JC_INTEGRITY_SALT)
    params["pp_SecureHash"] = secure_hash
    
    return {
        "action_url": "https://sandbox.jazzcash.com.pk/CustomerPortal/transactionmanagement/merchantform/",
        "params": params
    }

@router.post("/callback")
async def payment_callback(request: Request, db: AsyncSession = Depends(database.get_db)):
    form_data = await request.form()
    data = dict(form_data)
    
    response_code = data.get("pp_ResponseCode")
    txn_ref = data.get("pp_TxnRefNo")
    
    result = await db.execute(select(models.Payment).where(models.Payment.transaction_id == txn_ref))
    payment = result.scalars().first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
        
    if response_code == "000":
        payment.status = "success"
        result_user = await db.execute(select(models.User).where(models.User.id == payment.user_id))
        user = result_user.scalars().first()
        if user:
            user.is_paid = True
            db.add(user)
    else:
        payment.status = "failed"
        
    await db.commit()
    return {"status": "received"}
