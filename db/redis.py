from redis import Redis
from core.config import REDIS_URL

redis_client: Redis = Redis.from_url(REDIS_URL, decode_responses=True)

def invalidate_cache_by_pattern(r: Redis, match: str, *, count: int = 500, batch_size: int = 500) -> int:
    deleted = 0
    batch: list[str] = []

    try:
        for key in r.scan_iter(match=match, count=count):
            batch.append(key)

            if len(batch) >= batch_size:
                deleted += _delete_batch(r, batch)
                batch.clear()

        if batch:
            deleted += _delete_batch(r, batch)
            batch.clear()
    
    except Exception:
        return 0
    
    return deleted

def _delete_batch(r: Redis, keys: list[str]) -> int:
    if not keys:
        return 0
    
    try:
        r.unlink(*keys)
    except Exception:
        try:
            r.delete(*keys)
        except Exception:
            return 0
    
    return len(keys)
