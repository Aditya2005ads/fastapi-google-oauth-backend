from sqlmodel import SQLModel, Field
from typing import Optional
import datetime
from enum import Enum

class Customers(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    google_id: str = Field(unique=True)
    name: str = Field(nullable=False)
    age: Optional[int] = Field(default=None)
      
class PaymentStatus(str, Enum):
    PASS="pass"
    FAIL="fail"
class PaymentType(str, Enum):
    CARD="card"
    UPI="UPI"
class Payments(SQLModel, table=True):
    transaction_id: Optional[int] = Field(default=None, primary_key=True)
    status: PaymentStatus = Field(nullable=False)
    payment_type: PaymentType = Field(nullable=False)
    amount: float = Field(default=0.0, ge=0)
    currency: str = Field(default="INR")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))
    customer_id: int = Field(foreign_key="customers.id")

class OrderFoodItem(str, Enum):
    VEG_MANCHURIAN="Veg Manchurian"
    CHICKEN_MANCHURIAN="Chicken Manchurian"
    VEG_FRIED_RICE="Veg Fried Rice"
    CHICKEN_FRIED_RICE="Chicken Fried Rice"
class Orders(SQLModel, table=True):
    order_id: Optional[int] = Field(default=None, primary_key=True)
    item_name: OrderFoodItem = Field(nullable=False)
    transaction_id: int = Field(foreign_key="payments.transaction_id")
    restaurant_id: int = Field(foreign_key="restaurants.restaurant_id")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))
    customer_id: int = Field(foreign_key="customers.id")

class RestaurantAreaName(str, Enum):
    MUMBAI="Mumbai"
    BANGALORE="Bangalore"
class Restaurants(SQLModel, table=True):
    restaurant_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    area: RestaurantAreaName = Field(nullable=False)
