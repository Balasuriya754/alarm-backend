from fastapi import APIRouter, HTTPException, Depends
from models.models import AlarmCreate, AlarmUpdate
from db import alarm_collection, user_collection
from datetime import datetime, timezone
import uuid
from utils.auth_utils import verify_session


router = APIRouter(tags=["Alarms"])


# create alarm
@router.post("/alarms")
async def create_alarm(alarm:AlarmCreate,phone_num:str = Depends(verify_session)):
    user =  await user_collection.find_one({"phone_num":phone_num})
    if not user:
        raise HTTPException(status_code=404, detail="user not found!")

     
    alarm_doc = {
        "alarm_id": str(uuid.uuid4()),
        "event_id" : alarm.event_id,
        "phone_num": phone_num, ##
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
@router.get("/alarms")
async def get_alarm(phone_num: str = Depends(verify_session)):
    alarms = []
    async for alarm in alarm_collection.find({"phone_num":phone_num},{"_id":0}):
        
        alarms.append(alarm)

    return alarms


#update alarm
@router.put("/alarms/{event_id}" )
async def update_alarm(event_id: str, alarm: AlarmUpdate, phone_num:str = Depends(verify_session)):
    
    
    result = await alarm_collection.update_one(
        {"event_id":event_id,"phone_num":phone_num},
        {
           "$set":{
               "time":alarm.time,
               "label":alarm.label or "Not Defined",
               "enabled": alarm.enabled,
               "event_id":alarm.event_id,
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
@router.patch("/alarms/{event_id}")
async def toogle_alarm(event_id:str,phone_num:str = Depends(verify_session)):
    alarm = await alarm_collection.find_one({"event_id":event_id,"phone_num":phone_num})

    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    
    new_status = not alarm["enabled"]

    await alarm_collection.update_one(
        {"event_id":event_id,"phone_num":phone_num},
        {"$set": {"enabled": new_status,
                  "updated_at": datetime.now(timezone.utc)
                  }}
    )

    return {
        "event_id": event_id,
        "enabled": new_status
    }

#delete alarm
@router.delete("/alarms/{event_id}")
async def delete_alarm(event_id:str,phone_num:str = Depends(verify_session)):
    result = await alarm_collection.delete_one(
        {"event_id":event_id,"phone_num":phone_num},
    )

    if result.deleted_count==0:
        raise HTTPException(status_code=404, detail="Alarm not found")


    return {
        "message": "Alarm deleted",
       
    }

    