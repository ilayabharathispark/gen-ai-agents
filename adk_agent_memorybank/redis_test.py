# test_redis.py
import os
import redis
from dotenv import load_dotenv

load_dotenv()

r = redis.from_url(os.getenv("REDIS_URL"))

# Ping
print(r.ping())          # → True

# Test set/get
r.set("test_key", "hello from agent!", ex=60)   # ex=60 → TTL of 60 seconds
print(r.get("test_key"))                         # → b'hello from agent!'
print(r.ttl("test_key"))                         # → ~60 seconds remaining

print("✅ Redis Cloud connected successfully!")
