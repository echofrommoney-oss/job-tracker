import uuid
from typing import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import safe_delete
from app.models.job import Job, JobStatus
from app.models.status_history import StatusHistory
from app.schemas.job import JobCreate, JobUpdate

DASHBOARD_CACHE_KEY = "dashboard:stats"


async def _invalidate_dashboard_cache() -> None:
    await safe_delete(DASHBOARD_CACHE_KEY)


async def create_job(db: AsyncSession, payload: JobCreate) -> Job:
    job = Job(**payload.model_dump())
    db.add(job)
    await db.flush()

    history = StatusHistory(job_id=job.id, from_status=None, to_status=job.status)
    db.add(history)

    await db.commit()
    await db.refresh(job)
    await _invalidate_dashboard_cache()
    return job


async def list_jobs(
    db: AsyncSession,
    status: JobStatus | None = None,
    search: str | None = None,
) -> Sequence[Job]:
    stmt = select(Job)
    if status is not None:
        stmt = stmt.where(Job.status == status)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(or_(Job.company.ilike(pattern), Job.position.ilike(pattern)))
    stmt = stmt.order_by(Job.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_job(db: AsyncSession, job_id: uuid.UUID) -> Job | None:
    result = await db.execute(select(Job).where(Job.id == job_id))
    return result.scalar_one_or_none()


async def update_job(
    db: AsyncSession, job_id: uuid.UUID, payload: JobUpdate
) -> Job | None:
    job = await get_job(db, job_id)
    if job is None:
        return None

    data = payload.model_dump(exclude_unset=True)
    new_status = data.pop("status", None)

    for field, value in data.items():
        setattr(job, field, value)

    if new_status is not None and new_status != job.status:
        history = StatusHistory(
            job_id=job.id, from_status=job.status, to_status=new_status
        )
        db.add(history)
        job.status = new_status

    await db.commit()
    await db.refresh(job)
    await _invalidate_dashboard_cache()
    return job


async def delete_job(db: AsyncSession, job_id: uuid.UUID) -> bool:
    job = await get_job(db, job_id)
    if job is None:
        return False
    await db.delete(job)
    await db.commit()
    await _invalidate_dashboard_cache()
    return True


async def get_job_history(
    db: AsyncSession, job_id: uuid.UUID
) -> Sequence[StatusHistory] | None:
    job = await get_job(db, job_id)
    if job is None:
        return None
    stmt = (
        select(StatusHistory)
        .where(StatusHistory.job_id == job_id)
        .order_by(StatusHistory.changed_at)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def count_jobs(db: AsyncSession) -> int:
    result = await db.execute(select(func.count(Job.id)))
    return int(result.scalar_one())
