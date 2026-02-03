import random
#from passlib.context import CryptContext

#pwd_context = CryptContext(schemes=["bcrypt"], deprecated ="auto")


def generate_otp() -> str:
    return str(random.randint(1000,9999))

# def hash_otp(otp:str)->str:
#     return pwd_context.hash(otp)

# def verify_otp(plain_otp:str, hashed_otp:str)->bool:
#     return pwd_context.verify(plain_otp, hashed_otp)