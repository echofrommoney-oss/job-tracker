import pytest


@pytest.mark.asyncio
async def test_dashboard_empty_returns_zero_totals(client):
    response = await client.get("/api/v1/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["response_rate"] == 0.0
    assert data["avg_days_to_response"] is None


@pytest.mark.asyncio
async def test_dashboard_counts_jobs_by_status(client):
    await client.post(
        "/api/v1/jobs", json={"company": "A", "position": "X", "status": "applied"}
    )
    await client.post(
        "/api/v1/jobs", json={"company": "B", "position": "Y", "status": "interview"}
    )
    await client.post(
        "/api/v1/jobs", json={"company": "C", "position": "Z", "status": "rejected"}
    )
    response = await client.get("/api/v1/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["by_status"]["applied"] == 1
    assert data["by_status"]["interview"] == 1
    assert data["by_status"]["rejected"] == 1
    assert data["response_rate"] > 0


@pytest.mark.asyncio
async def test_dashboard_invalidates_cache_on_create(client):
    first = await client.get("/api/v1/dashboard")
    assert first.json()["total"] == 0

    await client.post(
        "/api/v1/jobs", json={"company": "A", "position": "X", "status": "applied"}
    )

    second = await client.get("/api/v1/dashboard")
    assert second.json()["total"] == 1
