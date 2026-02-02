from fastapi import APIRouter, HTTPException,Depends
from db import user_collection
from models.models import UserDetails
from datetime import timezone,datetime
from utils.auth_utils import verify_session


router = APIRouter(
    prefix="/user",
    tags= ["Users"],
    
)



#create user
@router.post("/")
async def create_user(user:UserDetails, phone_num: str = Depends(verify_session)):
   existing_user = await user_collection.find_one({"phone_num":phone_num})
   if existing_user:
       raise HTTPException(status_code=409, detail="user already registered")
   
   await user_collection.insert_one({
       "username": user.username,
       "phone_num": phone_num,
       "created_at": datetime.now(timezone.utc)

   })

  
   return {"message":"user stored successfully"}



# get user profile
@router.get("/me")
async def get_my_profile(phone_num: str = Depends(verify_session)):
    user = await user_collection.find_one({
        "phone_num":phone_num} ,
       {"_id": 0
        
    })
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


           
   
    
    

