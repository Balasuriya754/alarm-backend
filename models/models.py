from pydantic import BaseModel
from datetime import datetime

class UserDetails(BaseModel):
    username : str
    phone_num : str


class LoginModel(BaseModel):
    phone_num : str


class AlarmCreate(BaseModel):
    phone_num: str
    time: datetime # Example - 2026-01-26T07:30:00
    label: str
    enabled : bool = True

    

class AlarmUpdate(BaseModel):
    time: datetime
    label: str
    enabled: bool

