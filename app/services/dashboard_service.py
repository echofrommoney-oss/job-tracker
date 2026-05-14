import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import safe_get, safe_set
from app.models.job import Job, JobStatus
from app.models.status_history import StatusHistory
from app.schemas.dashboard import DashboardStats

logger = logging.getLogger(__name__)

CACHE_KEY = "dashboard:stats"
CACHE_TTL_SECONDS = 60

_RESPONSE_STATUSES = (JobStatus.interview, JobStatus.offer, JobStatus.rejected)


async def _compute_stats(db: AsyncSession) -> DashboardStats:
    count_stmt = select(Job.status, func.count(Job.id)).group_by(Job.status)
    result = await db.execute(count_stmt)
    counts: dict[JobStatus, int] = {status: 0 for status in JobStatus}
    total = 0
    for status, count in result.all():
        counts[status] = int(count)
        total += int(count)

    applied_count = counts[JobStatus.applied]
    response_count = sum(counts[s] for s in _RESPONSE_STATUSES)
    denom = applied_count + response_count
    response_rate = (response_count / denom * 100.0) if denom > 0 else 0.0

    first_change_stmt = (
        select(
            StatusHistory.job_id,
            func.min(StatusHistory.changed_at).label("first_change"),
        )
        .where(StatusHistory.from_status.isnot(None))
        .group_by(StatusHistory.job_id)
        .subquery()
    )
    avg_stmt = select(
        func.avg(
            func.extract(
                "epoch", first_change_stmt.c.first_change - Job.applied_at
            )
            / 86400.0
        )
    ).select_from(
        Job.__table__.join(first_change_stmt, Job.id == first_change_stmt.c.job_id)
    ).where(Job.applied_at.isnot(None))
    avg_result = await db.execute(avg_stmt)
    avg_value = avg_result.scalar_one_or_none()
    avg_days = float(avg_value) if avg_value is not None else None

    return DashboardStats(
        total=total,
        by_status=counts,
        response_rate=round(response_rate, 2),
        avg_days_to_response=round(avg_days, 2) if avg_days is not None else None,
    )


async def get_dashboard_stats(db: AsyncSession) -> DashboardStats:
    cached = await safe_get(CACHE_KEY)
    if cached is not None:
        try:
            return DashboardStats.model_validate_json(cached)
        except Exception as exc:
            logger.warning("Failed to parse cached dashboard stats: %s", exc)

    stats = await _compute_stats(db)
    await safe_set(CACHE_KEY, stats.model_dump_json(), ttl=CACHE_TTL_SECONDS)
    return stats
