from redis import Redis

class RedisHelper():

    def __init__(self, host: str):

        self.host = host
        self.redis_connection = self.create_redis_connection(self.host)

    def create_redis_connection(self, host) -> Redis:
        return Redis(host=host)

    def get_redis_keys(self, redis_keys: str):
        return self.redis_connection.keys(redis_keys)

    def delete_redis_keys(self, **redis_keys: str):
        return self.redis_connection.delete(**redis_keys)