import argparse
import redis
import atexit
import time
import socket


class SyncRedis():
    """Handle Redis Connection"""

    def __init__(self, redis_host: str, redis_port: int,
                 redis_password: str) -> None:
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.redis_sync_client = redis.Redis(host=self.redis_host,
                                             port=self.redis_port,
                                             password=self.redis_password,
                                             decode_responses=True)
        atexit.register(self.close_redis_pool)

    def close_redis_pool(self):
        if self.redis_sync_client is not None:
            self.redis_sync_client.close()
            print("RedisPool realse")


class SyncRedisHandler(SyncRedis):

    def __init__(self, redis_port: int, redis_password: str, triton_port: int,
                 process_uuid: str, redis_host: str) -> None:
        super().__init__(redis_host, redis_port, redis_password)
        self.triton_port = triton_port
        self.process_uuid = process_uuid

    def is_triton_alive(self) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', self.triton_port)) == 0

    def start_heartbeat(self):
        while (True):
            status = "connection" if self.is_triton_alive() else "wait"
            self.redis_sync_client.setex(self.process_uuid, 5, status)
            time.sleep(1)


def build_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--redis-ip",
                        default="127.0.0.1",
                        type=str,
                        help="the IP address of the redis")
    parser.add_argument("--redis-port",
                        required=True,
                        type=str,
                        help="the port number of the redis")
    parser.add_argument("--redis-password",
                        required=True,
                        type=str,
                        help="the password of the redis")
    parser.add_argument("--process-uuid",
                        required=True,
                        type=str,
                        help="the process-uuid of the triton server")
    parser.add_argument("--triton-port",
                        required=True,
                        type=int,
                        help="the port number of the triton server")
    return parser.parse_args()


if __name__ == "__main__":
    """python3 main.py --redis-port 8786 --redis-password admin --triton-port 8788 --process-uuid test"""
    args = build_arguments()
    sync_redis_client = SyncRedisHandler(
        redis_host=args.redis_ip,
        redis_port=args.redis_port,
        redis_password=args.redis_password,
        triton_port=args.triton_port,
        process_uuid=args.process_uuid)
    sync_redis_client.start_heartbeat()
