import boto3
import os

sns_client = boto3.client(
    "sns",
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),

)

def send_sms(phone_number:str, message:str):
    sns_client.publish(PhoneNumber= phone_number, Message = message)