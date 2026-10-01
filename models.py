from dataclasses import dataclass


@dataclass
class Driver:
    driver_id:str
    name:str
    zone:str
    available:bool
    rating: float

@dataclass
class Task:
    id:str
    customer:str
    zone:str
    distance:int
    order_amount:int
    priority:str
    status:str
    driver_id: str | None=None




