import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import ping as redis_ping
from app.dependencies import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)) -> dict[str, str | bool]:
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:
        logger.warning("Health DB check failed: %s", exc)

    redis_ok = await redis_ping()
    status_value = "ok" if db_ok and redis_ok else "degraded"
    return {"status": status_value, "database": db_ok, "redis": redis_ok}
