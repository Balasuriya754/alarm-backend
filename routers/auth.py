from fastapi import APIRouter, HTTPException
from utils.otp_utils import generate_otp
from services.sns_service import send_sms
from models.models import SendOTPRequest, VerifyOTPRequest
from db import user_collection, otp_collection
from datetime import timezone, datetime,timedelta
from redis_client import redis_client
import uuid

SESSION_TTL = 5 * 24 * 60 * 60


    
router = APIRouter(prefix="/auth", tags=["Auth"])

MAX_RESENDS =3
RESEND_WINDOW = timedelta(hours = 1)

@router.post("/send-otp")
async def send_otp(payload: SendOTPRequest):
    now = datetime.now(timezone.utc)

    
    user = await user_collection.find_one({"phone_num": payload.phone_num})

    if payload.flow == "register" and user:
        raise HTTPException(
            status_code=409,
            detail="User already registered. Please login."
        )

    if payload.flow == "login" and not user:
        raise HTTPException(
            status_code=403,
            detail="User not registered. Please register first."
        )

    
    record = await otp_collection.find_one({"phone_num": payload.phone_num})
    resend_count = 0
    window_start = now
    
    flow=payload.flow

    if record:
        resend_count = record.get("resend_count", 0)
        window_start = record.get("resend_window_start", now)
        if window_start.tzinfo is None:
            window_start = window_start.replace(tzinfo=timezone.utc)

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
                "otp": otp, #hash_otp(otp)
                "expires_at": now + timedelta(minutes=5),
                "attempts_left": 3,
                "resend_window_start": window_start,
                "created_at": now
            },
            "$inc": {"resend_count": 1}
        },
        upsert=True
    )

    send_sms(
        f"+91{payload.phone_num}",
        f"Your Alarm App OTP is {otp}. Valid for 5 minutes."
    )

    return {"message": "OTP sent successfully"}


 

@router.post("/verify-otp")
async def verify_user_otp(payload: VerifyOTPRequest):
    now = datetime.now(timezone.utc)
    phone_num = payload.phone_num
    flow=payload.flow
    record = await otp_collection.find_one({"phone_num":payload.phone_num})

    record = await otp_collection.find_one({"phone_num": phone_num})
    if not record:
        raise HTTPException(400, "OTP not found")
    
    expires_at = record["expires_at"]

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo = timezone.utc)

    if now > expires_at:
        await otp_collection.delete_one({"phone_num": phone_num})
        raise HTTPException(400, "OTP expired")
    
    if record["attempts_left"] <= 0:
        raise HTTPException(400, "OTP attempts exceeded")

    #if not verify_otp(payload.otp, record["otp_hash"]):
    if payload.otp != record["otp"]:
        await otp_collection.update_one(
            {"phone_num": phone_num},
            {"$inc": {"attempts_left": -1}}
        )
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    user = await user_collection.find_one({"phone_num":phone_num})
    if flow == 'register':
        if not user:
            await user_collection.insert_one({
                "phone_num": payload.phone_num,
                "created_at":datetime.now(timezone.utc)
            })
        else:
            raise HTTPException(status_code=400,detail="User already registered")
    
    if flow == "login":
        if not user:
            raise HTTPException(status_code=400,detail="User not registered")
        else:
            pass

    # CREATE SESSION 
    session_token = str(uuid.uuid4())

    try:
        old_token = redis_client.get(f"user_session:{phone_num}")
        if old_token:
            redis_client.delete(f"session:{old_token}")

        redis_client.setex(f"session:{session_token}",
                           SESSION_TTL, phone_num)
        
        redis_client.setex(f"user_session:{phone_num}",
                           SESSION_TTL,
                           session_token)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=503, detail="Authentication service is temporarily unavailable auth")
    
    

    redis_client.setex(f"session:{session_token}", SESSION_TTL, phone_num)
    redis_client.setex(f"user_session:{phone_num}", SESSION_TTL, session_token)

    return {"message": "OTP verified successfully",
            "session_token": session_token,
            "token_type": "Bearer"}

