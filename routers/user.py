from fastapi import APIRouter, HTTPException,Depends
from db import user_collection,alarm_collection,otp_collection
from models.models import UserDetails
from datetime import timezone,datetime
from utils.auth_utils import verify_session
from redis_client import redis_client


router = APIRouter(
    prefix="/user",
    tags= ["Users"],
    
)



#create user
@router.post("/")
async def create_user(
    user: UserDetails,
    phone_num: str = Depends(verify_session)
):
    existing_user = await user_collection.find_one({"phone_num": phone_num})
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="User already registered"
        )

    await user_collection.insert_one({
        "username": user.username,
        "phone_num": phone_num,
        "created_at": datetime.now(timezone.utc)
    })

    return {"message": "User registered successfully"}


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


#delete user complete account
@router.delete("/me")
async def delete_my_account(
    phone_num: str = Depends(verify_session)
):
    user = await user_collection.find_one({"phone_num": phone_num})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    
    await user_collection.delete_one({"phone_num": phone_num})

    await alarm_collection.delete_many({"phone_num": phone_num})

    
    await otp_collection.delete_many({"phone_num": phone_num})

    token = redis_client.get(f"user_session:{phone_num}")
    if token:
        redis_client.delete(f"session:{token.decode()}")
    redis_client.delete(f"user_session:{phone_num}")

    return {
        "message": "User account deleted successfully"
    }



           
   
    
    

