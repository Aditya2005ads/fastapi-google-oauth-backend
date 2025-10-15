from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from App.database import get_session
from App.models import (
    Orders,
    Payments,
    Restaurants,
    PaymentStatus,
    OrderFoodItem,
    RestaurantAreaName,
)
from App.schemas import EarningsResult, TopCustomer, DailyRevenue, ItemCount
from App.utils import get_current_user


router = APIRouter(prefix="/analytics", tags=["Analytics"], dependencies=[Depends(get_current_user)])


"""Assumption: One payment per order. If a payment maps to multiple orders, sums may double count."""


# 1. Total earnings of restaurants in Mumbai last month
@router.get("/earnings/mumbai-last-month", response_model=EarningsResult)
def earnings_mumbai_last_month(session: Session = Depends(get_session)):
    now = datetime.utcnow()
    first_of_this_month = datetime(now.year, now.month, 1)
    last_month_end = first_of_this_month - timedelta(seconds=1)
    first_of_last_month = datetime(last_month_end.year, last_month_end.month, 1)

    stmt = (
        select(func.coalesce(func.sum(Payments.amount), 0.0))
        .select_from(Orders)
        .join(Payments, Payments.transaction_id == Orders.transaction_id)
        .join(Restaurants, Restaurants.restaurant_id == Orders.restaurant_id)
        .where(Payments.status == PaymentStatus.PASS)
        .where(Restaurants.area == RestaurantAreaName.MUMBAI)
        .where(Orders.created_at >= first_of_last_month)
        .where(Orders.created_at <= last_month_end)
    )
    total = session.exec(stmt).one() or 0.0
    return EarningsResult(total_amount=float(total), currency="INR")


# 2. Total earnings from veg items in Bangalore
@router.get("/earnings/veg-bangalore", response_model=EarningsResult)
def earnings_veg_bangalore(session: Session = Depends(get_session)):
    veg_items = [OrderFoodItem.VEG_MANCHURIAN, OrderFoodItem.VEG_FRIED_RICE]
    stmt = (
        select(func.coalesce(func.sum(Payments.amount), 0.0))
        .select_from(Orders)
        .join(Payments, Payments.transaction_id == Orders.transaction_id)
        .join(Restaurants, Restaurants.restaurant_id == Orders.restaurant_id)
        .where(Payments.status == PaymentStatus.PASS)
        .where(Restaurants.area == RestaurantAreaName.BANGALORE)
        .where(Orders.item_name.in_(veg_items))
    )
    total = session.exec(stmt).one() or 0.0
    return EarningsResult(total_amount=float(total), currency="INR")


# 3. Top 3 customers with most orders placed
@router.get("/top-customers", response_model=List[TopCustomer])
def top_customers(session: Session = Depends(get_session)):
    from App.models import Customers  # local import to avoid cycles

    stmt = (
        select(Customers.name, func.count(Orders.order_id).label("orders_count"))
        .join(Orders, Orders.customer_id == Customers.id)
        .group_by(Customers.id)
        .order_by(func.count(Orders.order_id).desc())
        .limit(3)
    )
    rows = session.exec(stmt).all()
    return [TopCustomer(name=name, orders_count=cnt) for name, cnt in rows]


# 4. Daily revenue for past 7 days per city
@router.get("/daily-revenue", response_model=List[DailyRevenue])
def daily_revenue(session: Session = Depends(get_session)):
    start_date = datetime.utcnow().date() - timedelta(days=6)
    stmt = (
        select(
            func.date(Orders.created_at).label("date"),
            Restaurants.area,
            func.coalesce(func.sum(Payments.amount), 0.0).label("total_amount"),
        )
        .select_from(Orders)
        .join(Payments, Payments.transaction_id == Orders.transaction_id)
        .join(Restaurants, Restaurants.restaurant_id == Orders.restaurant_id)
        .where(Payments.status == PaymentStatus.PASS)
        .where(func.date(Orders.created_at) >= start_date)
        .group_by(func.date(Orders.created_at), Restaurants.area)
        .order_by(func.date(Orders.created_at))
    )
    rows = session.exec(stmt).all()
    return [
        DailyRevenue(date=str(date), area=area, total_amount=float(total), currency="INR")
        for date, area, total in rows
    ]


# 5. Orders summary for a specific restaurant (Total orders by item name and count)
@router.get("/restaurant/{restaurant_id}/items-summary", response_model=List[ItemCount])
def orders_summary_by_restaurant(restaurant_id: int, session: Session = Depends(get_session)):
    stmt = (
        select(Orders.item_name, func.count(Orders.order_id).label("count"))
        .where(Orders.restaurant_id == restaurant_id)
        .group_by(Orders.item_name)
    )
    rows = session.exec(stmt).all()
    return [ItemCount(item_name=item, count=cnt) for item, cnt in rows]

