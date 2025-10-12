from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select

from App.database import get_session
from App.models import Payments
from App.schemas import PaymentCreate, PaymentRead
from App.utils import get_current_user


router = APIRouter(prefix="/payments", tags=["Payments"], dependencies=[Depends(get_current_user)])


@router.post("/", response_model=PaymentRead)
def create_payment(payload: PaymentCreate, session: Session = Depends(get_session), user=Depends(get_current_user)):
    payment = Payments(
        status=payload.status,
        payment_type=payload.payment_type,
        amount=payload.amount,
        currency=payload.currency,
        customer_id=user.id,
    )
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment


@router.get("/", response_model=List[PaymentRead])
def list_payments(session: Session = Depends(get_session), user=Depends(get_current_user)):
    payments = session.exec(select(Payments).where(Payments.customer_id == user.id)).all()
    return payments


@router.get("/{transaction_id}", response_model=PaymentRead)
def get_payment(transaction_id: int, session: Session = Depends(get_session), user=Depends(get_current_user)):
    payment = session.get(Payments, transaction_id)
    if not payment or payment.customer_id != user.id:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

