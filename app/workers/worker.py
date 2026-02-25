import redis
from rq import Worker, Queue, Connection
from app.core.config import settings

listen = ["default"]

def main():
    redis_conn = redis.from_url(settings.redis_url)
    with Connection(redis_conn):
        worker = Worker(map(Queue, listen))
        worker.work()

if __name__ == "__main__":
    main()