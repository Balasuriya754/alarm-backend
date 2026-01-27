from pydantic import BaseModel
from datetime import datetime

class UserDetails(BaseModel):
    username : str
    phone_num : str
    password : str

class LoginModel(BaseModel):
    phone_num : str
    password: str

class AlarmCreate(BaseModel):
    user_id:str
    time: datetime # Example - 2026-01-26T07:30:00
    labeled: str
    enabled : bool = True
    

class AlarmUpdate(BaseModel):
    time: datetime
    label: str
    enabled: bool

