import sqlmodel
from sqlmodel import SQLModel,Session
from App.models import Customers, Payments, Orders, Restaurants

engine = sqlmodel.create_engine("sqlite:///database.db", echo=False)

def init_db():
    """Initialize the database."""
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session