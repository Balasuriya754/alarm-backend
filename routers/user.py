from fastapi import APIRouter, HTTPException
from db import user_collection
from models.models import UserDetails, LoginModel
from datetime import timezone,datetime


router = APIRouter(
    prefix="/user",
    tags= ["Users"]
)



#create user
@router.post("/")
async def create_user(user:UserDetails):
   existing_user = await user_collection.find_one({"phone_num":user.phone_num})
   if existing_user:
       raise HTTPException(status_code=409, detail="user already registered")
   
   await user_collection.insert_one({
       "username": user.username,
       "phone_num": user.phone_num,
       "created_at": datetime.now(timezone.utc)

   })

  
   return {"message":"user stored successfully"}


#login user
@router.post("/login",)
async def user_login(data: LoginModel):
    user = await user_collection.find_one({"phone_num":data.phone_num})

    if not user :
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"user_id":str(user["phone_num"])}

# get user profile
@router.get("/me")
async def get_my_profile(phone_num: str):
    user = await user_collection.find_one({
        "phone_num":phone_num} ,
       {"_id": 0
        
    })
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


           
   
    
    

