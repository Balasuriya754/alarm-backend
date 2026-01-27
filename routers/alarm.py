from fastapi import APIRouter, HTTPException
from models.models import AlarmCreate, AlarmUpdate
from bson import ObjectId
from db import alarm_collection
from datetime import datetime


router = APIRouter()


# create alarm
@router.post("/alarms" , tags=["Alarms"])
async def create_alarm(alarm:AlarmCreate):
    alarm_doc = {
        "user_id": ObjectId(alarm.user_id),
        "time": alarm.time,
        "labeled": alarm.labeled,
        "enabled":alarm.enabled
    }

    result = await alarm_collection.insert_one(alarm_doc)

    return{
        "message":"alarm created successfully",
        "alarm_id": str(result.inserted_id)
    }

# get alarms
@router.get("/alarms" , tags=["Alarms"])
async def get_alarm(user_id: str):
    alarms = []
    async for alarm in alarm_collection.find({"user_id":ObjectId(user_id)}):
        alarm["_id"] = str(alarm["_id"])
        alarm["user_id"] = str(alarm["user_id"])

        alarms.append(alarm)

    return alarms


#update alarm
@router.put("/alarms/{alarm_id}" , tags=["Alarms"])
async def update_alarm(alarm_id: str, alarm: AlarmUpdate):
    result = await alarm_collection.update_one(
        {"_id": ObjectId(alarm_id)},
        {
            "$set":{
                "time": alarm.time,
                "label":alarm.label,
                "enabled":alarm.enabled
            }
        }
    )

    if result.matched_count==0:
        raise HTTPException(status_code=404, detail="Alarm not found")
    
    return{
        "message": "Alarm updated",
        "alarm_id": alarm_id
    }

# toggle alarm
@router.patch("/alarms/{alarm_id}" , tags=["Alarms"])
async def toogle_alarm(alarm_id:str):
    alarm = await alarm_collection.find_one({"_id": ObjectId(alarm_id)})

    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    
    new_status = not alarm["enabled"]

    await alarm_collection.update_one(
        {"_id":ObjectId(alarm_id)},
        {"$set": {"enabled": new_status}}
    )

    return {
        "alarm_id": alarm_id,
        "enabled": new_status
    }

#delete alarm
@router.delete("/alarms/alarm_id" , tags=["Alarms"])
async def delete_alarm(alarm_id:str):
    result = await alarm_collection.delete_one(
        {"_id": ObjectId(alarm_id)},
    )

    if result.deleted_count==0:
        raise HTTPException(status_code=404, detail="Alarm not found")


    return {
        "message": "Alarm deleted",
        "alarm_id": alarm_id
    }

    