from pydantic import BaseModel

from app.models.job import JobStatus


class DashboardStats(BaseModel):
    total: int
    by_status: dict[JobStatus, int]
    response_rate: float
    avg_days_to_response: float | None
