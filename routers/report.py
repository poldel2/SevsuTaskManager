# routers/report_router.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from core.security import get_current_user
from dependencies import get_report_service
from models.schemas.reports import ReportResponse, ReportCreate
from services.report_service import ReportService


router = APIRouter(prefix="/project/{project_id}/report", tags=["report"])


@router.post("/", response_model=ReportResponse)
async def create_report(
    project_id: int,
    report: ReportCreate,
    report_service: ReportService = Depends(get_report_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        report_data = report.model_dump()
        return await report_service.create({**report_data, "project_id": project_id}, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Не удалось создать отчёт: " + str(e))


@router.get("/", response_model=List[ReportResponse])
async def get_reports(
    project_id: int,
    report_service: ReportService = Depends(get_report_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await report_service.get_reports_for_project(project_id, current_user.id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Не удалось получить список отчётов: " + str(e))


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report_by_id(
    project_id: int,  # не используется напрямую, но нужен для контекста URL
    report_id: int,
    report_service: ReportService = Depends(get_report_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await report_service.get_report(report_id, current_user.id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Не удалось получить отчёт: " + str(e))


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    project_id: int,
    report_id: int,
    report_update: ReportCreate,
    report_service: ReportService = Depends(get_report_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await report_service.update_report(report_id, report_update.model_dump(), current_user.id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Не удалось обновить отчёт: " + str(e))


@router.delete("/{report_id}")
async def delete_report(
    project_id: int,
    report_id: int,
    report_service: ReportService = Depends(get_report_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        result = await report_service.delete_report(report_id, current_user.id)
        return {"status": "success", "message": "Отчет успешно удален"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Не удалось удалить отчет: " + str(e))