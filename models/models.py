from pydantic import BaseModel
from datetime import datetime

class UserDetails(BaseModel):
    username : str
    phone_num : str


class LoginModel(BaseModel):
    phone_num : str


class AlarmCreate(BaseModel):
    phone_num: str
    time: int # Example - 2026-01-26T07:30:00
    label: str
    enabled : bool = True
    event_id : str

    

class AlarmUpdate(BaseModel):
    time: int
    label: str
    enabled: bool
    event_id : str

