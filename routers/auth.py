from fastapi import APIRouter, HTTPException
import http.client
import os
from db import user_collection
from datetime import timezone, datetime

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/send-otp")
async def send_otp(phone_num:str):
    auth_key = os.getenv("MSG91_AUTH_KEY")
    

    if not auth_key :
        raise HTTPException(status_code=500, detail= "Missing MSG91 Config")
    
    mobile = f"91{phone_num}"

    conn = http.client.HTTPSConnection("control.msg91.com")

    url = (
          f"/api/v5/otp?"
        f"authkey={auth_key}"
        f"&mobile={mobile}"

        f"&otp_length=4"
        
    )

    headers = { "Content-Type":"application/json"}

    try:
        conn.request("POST",url, headers=headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
    except Exception:
        raise HTTPException(status_code=500, detail = "Failed to connect to MSG91")
    

    if res.status != 200:
        raise HTTPException(status_code=500, detail="Failed to send OTP")
    
    return {
        "message":"OTP sent successfully",
        "phone_num":phone_num
    }

@router.post("/verify-otp")
async def verify_otp(phone_num:str, otp:str):
    auth_key = os.getenv("MSG91_AUTH_KEY")

    if not auth_key:
        raise HTTPException(status_code=500 , detail="MSG91 auth key is missing")
    
    mobile = f"91{phone_num}"

    conn = http.client.HTTPSConnection("control.msg91.com")

    url= (
         f"/api/v5/otp/verify?"
        f"authkey={auth_key}"
        f"&mobile={mobile}"
        f"&otp={otp}"
    )

    try:
        conn.request("GET",url)
        res = conn.getresponse()
        data = res.read().decode("utf-8")

    except Exception:
        raise HTTPException(status_code=500, detail="Failed to connect to MSG91")
    
    if res.status != 200:
        raise HTTPException(status_code=401, detail = "Invalid or expired OTP")
    
    user = await user_collection.find_one({"phone_num":phone_num})

    if not user:
        await user_collection.insert_one({
            "phone_num": phone_num,
            "created_at": datetime.now(timezone.utc)

        })
    return {
            "message": "OTP Verified successfully",
            "phone_num": phone_num
        }
    
@router.post("/resend-otp")
async def resend_otp(phone_num:str):

    auth_key = os.getenv("MSG91_AUTH_KEY")

    if not auth_key:
        raise HTTPException(status_code=500 , detail="MSG91 auth key is missing")
    
    mobile = f"91{phone_num}"

    conn = http.client.HTTPSConnection("control.msg91.com")

    url = (
         f"/api/v5/otp/retry?"
        f"authkey={auth_key}"
        f"&mobile={mobile}"
        f"&retrytype=text"
    )

    try:
        conn.request("GET", url)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
    except Exception:
        raise HTTPException(
            status_code= 500,detail="Failed to connect to MSG91"

        )
    
    if res.status != 200:
        raise HTTPException(status_code=400, detail= "Failed to resend OTP")

    return {
        "message": "OTP resend successfully",
        "phone_num":phone_num
    }
