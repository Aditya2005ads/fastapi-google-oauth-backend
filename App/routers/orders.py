from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select

from App.database import get_session
from App.models import Orders, Payments, PaymentStatus
from App.schemas import OrderCreate, OrderRead
from App.utils import get_current_user


router = APIRouter(prefix="/orders", tags=["Orders"], dependencies=[Depends(get_current_user)])


@router.post("/", response_model=OrderRead)
def create_order(payload: OrderCreate, session: Session = Depends(get_session), user=Depends(get_current_user)):
    # Verify payment exists, belongs to user, and is successful
    payment = session.get(Payments, payload.transaction_id)
    if session.exec(select(Orders).where(Orders.transaction_id == payload.transaction_id)).first():
        raise HTTPException(status_code=400, detail="Order with this transaction ID already exists")
    if not payment or payment.customer_id != user.id:
        raise HTTPException(status_code=400, detail="Invalid or unauthorized payment")
    if payment.status != PaymentStatus.PASS:
        raise HTTPException(status_code=400, detail="Payment not successful")

    order = Orders(
        item_name=payload.item_name,
        transaction_id=payload.transaction_id,
        restaurant_id=payload.restaurant_id,
        customer_id=user.id,
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.get("/", response_model=List[OrderRead])
def list_orders(session: Session = Depends(get_session), user=Depends(get_current_user)):
    orders = session.exec(select(Orders).where(Orders.customer_id == user.id)).all()
    return orders


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, session: Session = Depends(get_session), user=Depends(get_current_user)):
    order = session.get(Orders, order_id)
    if not order or order.customer_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

