from fastapi import APIRouter, HTTPException
from models.models import AlarmCreate, AlarmUpdate
from db import alarm_collection, user_collection
from datetime import datetime, timezone
import uuid


router = APIRouter()


# create alarm
@router.post("/alarms" , tags=["Alarms"])
async def create_alarm(alarm:AlarmCreate):
    user =  await user_collection.find_one({"phone_num":alarm.phone_num})
    if not user:
        raise HTTPException(status_code=404, detail="user not found!")

     
    alarm_doc = {
        "alarm_id": str(uuid.uuid4()),
        "phone_num": alarm.phone_num,
        "time": alarm.time,
        "label": alarm.label,
        "created_at": datetime.now(timezone.utc),
        "enabled":alarm.enabled,
        "updated_at":datetime.now(timezone.utc)
    }

    result = await alarm_collection.insert_one(alarm_doc)

    return{
        "message":"alarm created successfully",
        "alarm_id": alarm_doc["alarm_id"]
    }

# get alarms
@router.get("/alarms" , tags=["Alarms"])
async def get_alarm(phone_num: str):
    alarms = []
    async for alarm in alarm_collection.find({"phone_num":phone_num},{"_id":0}):
        
        alarms.append(alarm)

    return alarms


#update alarm
@router.put("/alarms/{alarm_id}" , tags=["Alarms"])
async def update_alarm(alarm_id: str, alarm: AlarmUpdate, phone_num:str):
    result = await alarm_collection.update_one(
        {"alarm_id":alarm_id,"phone_num":phone_num},
        {
           "$set":{
               "time":alarm.time,
               "label":alarm.label,
               "enabled": alarm.enabled,
               "updated_at":datetime.now(timezone.utc)
           }
            }
        
    )

    if result.matched_count==0:
        raise HTTPException(status_code=404, detail="Alarm not found")
    
    return{
        "message": "Alarm updated",
        
    }

# toggle alarm
@router.patch("/alarms/{alarm_id}" , tags=["Alarms"])
async def toogle_alarm(alarm_id:str,phone_num:str):
    alarm = await alarm_collection.find_one({"alarm_id":alarm_id,"phone_num":phone_num})

    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    
    new_status = not alarm["enabled"]

    await alarm_collection.update_one(
        {"alarm_id":alarm_id,"phone_num":phone_num},
        {"$set": {"enabled": new_status,
                  "updated_at": datetime.now(timezone.utc)
                  }}
    )

    return {
        "alarm_id": alarm_id,
        "enabled": new_status
    }

#delete alarm
@router.delete("/alarms/{alarm_id}" , tags=["Alarms"])
async def delete_alarm(alarm_id:str,phone_num:str):
    result = await alarm_collection.delete_one(
        {"alarm_id":alarm_id,"phone_num":phone_num},
    )

    if result.deleted_count==0:
        raise HTTPException(status_code=404, detail="Alarm not found")


    return {
        "message": "Alarm deleted",
       
    }

    