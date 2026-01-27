from fastapi import APIRouter, HTTPException
from bson import ObjectId
from db import user_collection
from models.models import UserDetails, LoginModel

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

   await user_collection.insert_one(user.model_dump())
   return {"message":"user stored successfully"}


#login user
@router.post("/login",)
async def user_login(data: LoginModel):
    user = await user_collection.find_one({"phone_num":data.phone_num})

    if not user or user["password"]!=data.password:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    return {"user_id":str(user["_id"])}

# get user profile
@router.get("/me")
async def get_my_profile(user_id: str):
    user = await user_collection.find_one({
        "_id":ObjectId(user_id)} ,
       {"_id": 0,
        "password": 0
    })

    return user


           
   
    
    

