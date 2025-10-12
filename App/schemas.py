from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel

from App.models import (
    PaymentStatus,
    PaymentType,
    OrderFoodItem,
    RestaurantAreaName,
)

# Common read models
class CustomerRead(SQLModel):
    id: int
    google_id: str
    name: str
    age: Optional[int] = None

# Restaurant
class RestaurantCreate(SQLModel):
    name: str
    area: RestaurantAreaName

class RestaurantUpdate(SQLModel):
    name: Optional[str] = None
    area: Optional[RestaurantAreaName] = None

class RestaurantRead(SQLModel):
    restaurant_id: int
    name: str
    area: RestaurantAreaName

# Payments
class PaymentCreate(SQLModel):
    status: PaymentStatus
    payment_type: PaymentType
    amount: float
    currency: str = "INR"

class PaymentRead(SQLModel):
    transaction_id: int
    status: PaymentStatus
    payment_type: PaymentType
    created_at: datetime
    customer_id: int
    amount: float
    currency: str

# Orders
class OrderCreate(SQLModel):
    item_name: OrderFoodItem
    transaction_id: int
    restaurant_id: int

class OrderRead(SQLModel):
    order_id: int
    item_name: OrderFoodItem
    transaction_id: int
    restaurant_id: int
    created_at: datetime
    customer_id: int

# Analytics schemas
class TopCustomer(SQLModel):
    name: str
    orders_count: int

class DailyCityOrders(SQLModel):
    date: str
    area: RestaurantAreaName
    orders_count: int

class ItemCount(SQLModel):
    item_name: OrderFoodItem
    count: int

class EarningsResult(SQLModel):
    total_amount: float
    currency: str

class DailyRevenue(SQLModel):
    date: str
    area: RestaurantAreaName
    total_amount: float
    currency: str
