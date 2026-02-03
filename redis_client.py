import redis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis") 
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(
    host="redis-10834.crce182.ap-south-1-1.ec2.cloud.redislabs.com",
    port=10834,
    decode_responses=True,
    username="default",
    password="d6bb1qvp1UNKHikBAkAHZxbBKLWPIy3l",
)
