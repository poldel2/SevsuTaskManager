import pytest
from httpx import AsyncClient
from datetime import datetime, date, timedelta
from models.domain.reports import Report
from .test_fixtures import auth_headers, project_id, TEST_PROJECT

TEST_REPORT = {
    "title": "Test Report",
    "period_start": (datetime.now() - timedelta(days=7)).date().isoformat(),
    "period_end": datetime.now().date().isoformat(),
    "data": {"completed_tasks": 10, "active_sprints": 2},
    "project_id": 1
}

@pytest.mark.asyncio
async def test_create_report(client: AsyncClient, auth_headers, project_id):
    report_data = {**TEST_REPORT, "project_id": project_id}
    response = await client.post(
        f"/project/{project_id}/report/",
        json=report_data,
        headers=auth_headers
    )
    assert response.status_code == 200, f"Got {response.status_code}: {response.json()}"
    data = response.json()
    assert data["title"] == TEST_REPORT["title"]
    assert data["project_id"] == project_id
    assert data["data"] == TEST_REPORT["data"]
    assert data["period_start"] == TEST_REPORT["period_start"]
    assert data["period_end"] == TEST_REPORT["period_end"]

@pytest.mark.asyncio
async def test_get_report(client: AsyncClient, auth_headers, project_id):
    report_data = {**TEST_REPORT, "project_id": project_id}
    response = await client.post(
        f"/project/{project_id}/report/",
        json=report_data,
        headers=auth_headers
    )
    report_id = response.json()["id"]

    response = await client.get(
        f"/project/{project_id}/report/{report_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == report_id
    assert data["title"] == TEST_REPORT["title"]
    assert data["project_id"] == project_id

@pytest.mark.asyncio
async def test_get_project_reports(client: AsyncClient, auth_headers, project_id):
    report_data_1 = {**TEST_REPORT, "project_id": project_id}
    report_data_2 = {**TEST_REPORT, "title": "Second Report", "project_id": project_id}
    await client.post(f"/project/{project_id}/report/", json=report_data_1, headers=auth_headers)
    await client.post(f"/project/{project_id}/report/", json=report_data_2, headers=auth_headers)

    response = await client.get(
        f"/project/{project_id}/report/",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["project_id"] == project_id
    assert data[1]["project_id"] == project_id

@pytest.mark.asyncio
async def test_update_report(client: AsyncClient, auth_headers, project_id):
    report_data = {**TEST_REPORT, "project_id": project_id}
    response = await client.post(
        f"/project/{project_id}/report/",
        json=report_data,
        headers=auth_headers
    )
    report_id = response.json()["id"]

    update_data = {
        "title": "Updated Report",
        "period_start": (datetime.now() - timedelta(days=14)).date().isoformat(),
        "period_end": (datetime.now() - timedelta(days=1)).date().isoformat(),
        "data": {"completed_tasks": 15, "active_sprints": 3},
        "project_id": project_id
    }
    response = await client.put(
        f"/project/{project_id}/report/{report_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["data"] == update_data["data"]
    assert data["period_start"] == update_data["period_start"]
    assert data["period_end"] == update_data["period_end"]

@pytest.mark.asyncio
async def test_delete_report(client: AsyncClient, auth_headers, project_id):
    report_data = {**TEST_REPORT, "project_id": project_id}
    response = await client.post(
        f"/project/{project_id}/report/",
        json=report_data,
        headers=auth_headers
    )
    report_id = response.json()["id"]

    response = await client.delete(
        f"/project/{project_id}/report/{report_id}",
        headers=auth_headers
    )
    assert response.status_code == 204

    response = await client.get(
        f"/project/{project_id}/report/{report_id}",
        headers=auth_headers
    )
    assert response.status_code == 404