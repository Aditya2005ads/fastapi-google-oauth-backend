from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select

from App.database import get_session
from App.models import Restaurants
from App.schemas import RestaurantCreate, RestaurantRead, RestaurantUpdate
from App.utils import get_current_user


router = APIRouter(prefix="/restaurants", tags=["Restaurants"], dependencies=[Depends(get_current_user)])


@router.post("/", response_model=RestaurantRead)
def create_restaurant(payload: RestaurantCreate, session: Session = Depends(get_session)):
    restaurant = Restaurants(name=payload.name, area=payload.area)
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    return restaurant


@router.get("/", response_model=List[RestaurantRead])
def list_restaurants(session: Session = Depends(get_session)):
    restaurants = session.exec(select(Restaurants)).all()
    return restaurants


@router.get("/{restaurant_id}", response_model=RestaurantRead)
def get_restaurant(restaurant_id: int, session: Session = Depends(get_session)):
    restaurant = session.get(Restaurants, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.patch("/{restaurant_id}", response_model=RestaurantRead)
def update_restaurant(restaurant_id: int, payload: RestaurantUpdate, session: Session = Depends(get_session)):
    restaurant = session.get(Restaurants, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if payload.name is not None:
        restaurant.name = payload.name
    if payload.area is not None:
        restaurant.area = payload.area
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    return restaurant


@router.delete("/{restaurant_id}")
def delete_restaurant(restaurant_id: int, session: Session = Depends(get_session)):
    restaurant = session.get(Restaurants, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    session.delete(restaurant)
    session.commit()
    return {"message": "Deleted"}

