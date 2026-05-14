import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.job import JobStatus


class JobBase(BaseModel):
    company: str = Field(..., min_length=1, max_length=255)
    position: str = Field(..., min_length=1, max_length=255)
    job_url: str | None = Field(None, max_length=1024)
    description: str | None = None
    salary_min: int | None = Field(None, ge=0)
    salary_max: int | None = Field(None, ge=0)
    location: str | None = Field(None, max_length=255)
    notes: str | None = None
    applied_at: datetime | None = None

    @model_validator(mode="after")
    def _check_salary_range(self) -> "JobBase":
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("salary_min cannot be greater than salary_max")
        return self


class JobCreate(JobBase):
    status: JobStatus = JobStatus.wishlist


class JobUpdate(BaseModel):
    company: str | None = Field(None, min_length=1, max_length=255)
    position: str | None = Field(None, min_length=1, max_length=255)
    job_url: str | None = Field(None, max_length=1024)
    description: str | None = None
    status: JobStatus | None = None
    salary_min: int | None = Field(None, ge=0)
    salary_max: int | None = Field(None, ge=0)
    location: str | None = Field(None, max_length=255)
    notes: str | None = None
    applied_at: datetime | None = None


class JobResponse(JobBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: JobStatus
    created_at: datetime
    updated_at: datetime


class StatusHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    from_status: JobStatus | None
    to_status: JobStatus
    changed_at: datetime
