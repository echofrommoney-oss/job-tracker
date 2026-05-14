import pytest


@pytest.mark.asyncio
async def test_create_job_returns_201_and_full_payload(client):
    response = await client.post(
        "/api/v1/jobs",
        json={
            "company": "Acme Corp",
            "position": "Backend Engineer",
            "status": "applied",
            "salary_min": 100000,
            "salary_max": 140000,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["company"] == "Acme Corp"
    assert data["status"] == "applied"
    assert data["id"]


@pytest.mark.asyncio
async def test_create_job_with_invalid_salary_range_returns_422(client):
    response = await client.post(
        "/api/v1/jobs",
        json={
            "company": "Acme",
            "position": "Dev",
            "salary_min": 200000,
            "salary_max": 100000,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_jobs_filters_by_status(client):
    await client.post(
        "/api/v1/jobs",
        json={"company": "A", "position": "X", "status": "applied"},
    )
    await client.post(
        "/api/v1/jobs",
        json={"company": "B", "position": "Y", "status": "wishlist"},
    )
    response = await client.get("/api/v1/jobs", params={"status": "applied"})
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 1
    assert rows[0]["company"] == "A"


@pytest.mark.asyncio
async def test_list_jobs_search_by_company(client):
    await client.post(
        "/api/v1/jobs",
        json={"company": "Acme Corp", "position": "Engineer"},
    )
    await client.post(
        "/api/v1/jobs",
        json={"company": "Globex", "position": "Engineer"},
    )
    response = await client.get("/api/v1/jobs", params={"search": "acme"})
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 1
    assert rows[0]["company"] == "Acme Corp"


@pytest.mark.asyncio
async def test_get_job_not_found_returns_404(client):
    response = await client.get("/api/v1/jobs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_with_invalid_uuid_returns_422(client):
    response = await client.get("/api/v1/jobs/not-a-uuid")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_job_status_writes_history(client):
    created = await client.post(
        "/api/v1/jobs",
        json={"company": "A", "position": "X", "status": "applied"},
    )
    job_id = created.json()["id"]

    updated = await client.patch(
        f"/api/v1/jobs/{job_id}", json={"status": "interview"}
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "interview"

    history = await client.get(f"/api/v1/jobs/{job_id}/history")
    assert history.status_code == 200
    rows = history.json()
    assert len(rows) == 2
    assert rows[0]["from_status"] is None
    assert rows[0]["to_status"] == "applied"
    assert rows[1]["from_status"] == "applied"
    assert rows[1]["to_status"] == "interview"


@pytest.mark.asyncio
async def test_update_job_not_found_returns_404(client):
    response = await client.patch(
        "/api/v1/jobs/00000000-0000-0000-0000-000000000000",
        json={"status": "interview"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_job_returns_204_and_then_404(client):
    created = await client.post(
        "/api/v1/jobs", json={"company": "A", "position": "X"}
    )
    job_id = created.json()["id"]

    deleted = await client.delete(f"/api/v1/jobs/{job_id}")
    assert deleted.status_code == 204

    after = await client.get(f"/api/v1/jobs/{job_id}")
    assert after.status_code == 404


@pytest.mark.asyncio
async def test_history_not_found_returns_404(client):
    response = await client.get(
        "/api/v1/jobs/00000000-0000-0000-0000-000000000000/history"
    )
    assert response.status_code == 404
