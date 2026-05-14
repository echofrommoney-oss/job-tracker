import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.job import JobStatus
from app.schemas.job import JobCreate, JobResponse, JobUpdate, StatusHistoryResponse
from app.services import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobCreate, db: AsyncSession = Depends(get_db)
) -> JobResponse:
    job = await job_service.create_job(db, payload)
    return JobResponse.model_validate(job)


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    status_filter: JobStatus | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None, min_length=1, max_length=255),
    db: AsyncSession = Depends(get_db),
) -> list[JobResponse]:
    jobs = await job_service.list_jobs(db, status=status_filter, search=search)
    return [JobResponse.model_validate(j) for j in jobs]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> JobResponse:
    job = await job_service.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.model_validate(job)


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: uuid.UUID,
    payload: JobUpdate,
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    job = await job_service.update_job(db, job_id, payload)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.model_validate(job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    deleted = await job_service.delete_job(db, job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")


@router.get("/{job_id}/history", response_model=list[StatusHistoryResponse])
async def get_job_history(
    job_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[StatusHistoryResponse]:
    history = await job_service.get_job_history(db, job_id)
    if history is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return [StatusHistoryResponse.model_validate(h) for h in history]
