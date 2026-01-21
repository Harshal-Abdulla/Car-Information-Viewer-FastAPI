from fastapi import FastAPI, Query, Path, HTTPException, status, Body
from pydantic import BaseModel, Field
from fastapi.encoders import jsonable_encoder
from typing import Optional, List, Dict
from database import cars

class Car(BaseModel):
    make : Optional[str] = None
    model : Optional[str] = None
    year : Optional[int] = Field(None, ge=1970, lt=2026) #ge = >=, lt = <, ..., = we are ignoring the default field and just putting the required fields
    price : Optional[float] = None
    engine : Optional[str] = "V4"
    autonomous : Optional[bool] = None
    sold : Optional[List[str]] = None

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI"}

@app.get("/cars", response_model = List[Dict[str, Car]])
def get_cars(number : Optional[str] = Query("10", max_length=3)): #doesnt want to exceed 999
    response = []
    for id, car in list(cars.items())[:int(number)]:
        to_add = {}
        to_add[str(id)] = car
        response.append(to_add)
    return response

@app.get("/cars/{id}", response_model=Car)
def get_car_by_id(id: int = Path(...,ge=0, lt=1000)):
    car = cars.get(id)
    if not car:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Could not find car by id")
    return car

@app.post("/cars", status_code=status.HTTP_201_CREATED)
def add_car(body_cars:List[Car], min_id: Optional[int]=Body(0)):
    if len(body_cars)<1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= "No cars listed to add")
    min_id = len(cars.values()) + min_id
    for car in body_cars:
        while cars.get(min_id):
            min_id+=1
        cars[min_id] = car
        min_id +=1

@app.put("/cars/{id}", response_model=Dict[str, Car])
def update_car(id: int, car: Car = Body(...)):
    stored = cars.get(id)
    if not stored:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Could not find car with given ID.")
    stored = Car(**stored)
    new = car.dict(exclude_unset=True)
    new = stored.copy(update=new)
    cars[id] = jsonable_encoder(new)
    response = {}
    response[id] = cars[id]
    return response

@app.delete("/cars/{id}")
def delete_car(id: int):
    if not cars.get(id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Could not find car with given ID.")
    del cars[id]
