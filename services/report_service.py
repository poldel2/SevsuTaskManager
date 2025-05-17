from fastapi import HTTPException
from models.domain.reports import Report
from repositories.report_repository import ReportRepository
from services.project_service import ProjectService


class ReportService:
    def __init__(
        self,
        report_repository: ReportRepository,
        project_service: ProjectService,
    ):
        self.report_repository = report_repository
        self.project_service = project_service

    async def create(self, report_data: dict, current_user_id: int) -> Report:
        await self._check_project_access(report_data["project_id"], current_user_id)
        return await self.report_repository.create(report_data)

    async def get_report(self, report_id: int, current_user_id: int) -> Report:
        report = await self.report_repository.get_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Отчет не найден")
        await self._check_project_access(report.project_id, current_user_id)
        return report

    async def update_report(self, report_id: int, update_data: dict, current_user_id: int):
        report = await self.report_repository.get_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Отчет не найден")
        await self._check_project_access(report.project_id, current_user_id)
        return await self.report_repository.update(report_id, update_data)

    async def delete_report(self, report_id: int, current_user_id: int) -> bool:
        report = await self.report_repository.get_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Отчет не найден")
        await self._check_project_access(report.project_id, current_user_id)
        return await self.report_repository.delete(report_id)

    async def get_reports_for_project(self, project_id: int, current_user_id: int, limit: int = 50):
        await self._check_project_access(project_id, current_user_id)
        return await self.report_repository.get_reports_by_project(project_id, limit)

    async def _check_project_access(self, project_id: int, current_user_id: int):
        await self.project_service.validate_project_access(project_id, current_user_id)