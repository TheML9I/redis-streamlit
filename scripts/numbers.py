import os
import random
import time

import redis

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_password = os.getenv('REDIS_PASSWORD', 'localhost')

r = None

def get_redis_connection(max_retries=5, retry_delay=1):
    retries = 0
    while retries < max_retries:
        try:
            r = redis.Redis(host=redis_host, port=redis_port, password=redis_password)
            r.ping()
            print(f"Successfully connected to Redis at {redis_host}:{redis_port}")
            return r
        except redis.ConnectionError:
            retries += 1
            print(f"Connection attempt {retries}/{max_retries} failed. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    raise Exception(f"Could not connect to Redis at {redis_host}:{redis_port} after {max_retries} attempts")

def main():
    global r
    r = get_redis_connection()
    
    reverse_1to100()
    desc_random()

def reverse_1to100():
    key = "1_100_numbers"
    r.delete(key)
    
    print("Inserting values 1-100 into Redis sorted set...")
    for i in range(1, 101):
        r.zadd(key, {str(i): i})
    
    print("Retrieving values in reverse order...")
    reversed_numbers = r.zrevrange(key, 0, -1)
    
    print("Values in reverse order:")
    for num in reversed_numbers:
        print(num.decode())

def desc_random():
    key = "random_numbers"
    r.delete(key)
    
    print("Generating and inserting 100 random numbers into Redis sorted set...")
    
    random_numbers = {}
    while len(random_numbers) < 100:
        num = random.randint(1, 1000)
        random_numbers[str(num)] = num

    r.zadd(key, random_numbers)
    
    print("Retrieving values in descending order...")
    desc_numbers = r.zrevrange(key, 0, -1, withscores=True)
    
    print("Values in descending order:")
    for each, (value, score) in enumerate(desc_numbers, 1):
        print(f"#{each}: {int(score)}")

if __name__ == "__main__":
    main()