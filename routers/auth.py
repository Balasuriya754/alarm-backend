from fastapi import APIRouter, HTTPException
from utils.otp_utils import generate_otp, verify_otp,hash_otp
from services.sns_service import send_sms
from models.models import SendOTPRequest, VerifyOTPRequest
from db import user_collection, otp_collection
from datetime import timezone, datetime,timedelta

router = APIRouter(prefix="/auth", tags=["Auth"])

MAX_RESENDS =3
RESEND_WINDOW = timedelta(hours = 1)

@router.post("/send-otp")
async def send_otp(payload: SendOTPRequest):
    now = datetime.now(timezone.utc)

    record = await otp_collection.find_one(
        {"phone_num": payload.phone_num}
    )

    resend_count = 0
    window_start = now

    if record:
        resend_count = record.get("resend_count", 0)
        window_start = record.get("resend_window_start", now)

        if window_start.tzinfo is None:
            window_start= window_start.replace(tzinfo = timezone.utc)

        
        if now - window_start > RESEND_WINDOW:
            resend_count = 0
            window_start = now

        
        if resend_count >= MAX_RESENDS:
            raise HTTPException(
                status_code=429,
                detail="Too many OTP requests. Please try again later."
            )


    otp = generate_otp()

    
    await otp_collection.update_one(
        {"phone_num": payload.phone_num},
        {
            "$set": {
                "otp_hash": hash_otp(otp),
                "expires_at": now + timedelta(minutes=5),
                "attempts_left": 3,
                "resend_window_start": window_start,
                "created_at": now
            },
            "$inc": {
                "resend_count": 1
            }
        },
        upsert=True
    )

    
    send_sms(
        f"+91{payload.phone_num}",
        f"Your Alarm App OTP is {otp}. Valid for 5 minutes."
    )

    return {"message": "OTP sent successfully"}



 

@router.post("/verify-otp")
async def verify_user_otp(payload:VerifyOTPRequest):
    record = await otp_collection.find_one({"phone_num":payload.phone_num})

    if not record:
        raise HTTPException(400 , "OTP not found")
    
    expires_at = record["expires_at"]

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400 , detail="OTP expired")
    
    if record["attempts_left"]<=0:
        raise HTTPException(status_code=400, detail="OTP Attempts exceeded")
    
    if not verify_otp(payload.otp, record["otp_hash"]):
        await otp_collection.update_one(
            
                {"phone_num":payload.phone_num},
                {"$inc":{"attempts_left":-1}
            }
        )
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    user = await user_collection.find_one({"phone_num":payload.phone_num})
    if not user:
        await user_collection.insert_one({
            "phone_num": payload.phone_num,
            "created_at":datetime.now(timezone.utc)
        })

    await otp_collection.delete_one({"phone_num":payload.phone_num})

    return {"message": "OTP verified successfully"}

