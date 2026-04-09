from loguru import logger

from src.modules.seedwork.base_usecase import BaseUseCase, async_transactional
from src.modules.mr_analytics.usecase.fetch_mrs.impl import FetchMergeRequestsUseCase
from src.modules.mr_analytics.usecase.fetch_mrs.command import FetchMergeRequestsCommand
from src.modules.mr_analytics.usecase.process_mrs.impl import ProcessMergeRequestsUseCase
from src.modules.mr_analytics.usecase.process_mrs.command import ProcessMergeRequestsCommand
from src.modules.mr_analytics.usecase.run_analysis.command import (
    RunAnalysisCommand,
    RunAnalysisResponse
)


class RunAnalysisUseCase(BaseUseCase):
    
    def __init__(self, fetch_uc: FetchMergeRequestsUseCase, process_uc: ProcessMergeRequestsUseCase):
        self._fetch_uc = fetch_uc
        self._process_uc = process_uc
    
    @async_transactional()
    async def invoke(self, command: RunAnalysisCommand) -> RunAnalysisResponse:
        logger.info("=" * 60)
        logger.info(f"Starting full MR analysis for last {command.days} days")
        logger.info("=" * 60)
        
        fetch_command = FetchMergeRequestsCommand(days=command.days)
        fetch_result = await self._fetch_uc.invoke(fetch_command)
        
        if not fetch_result.mrs:
            logger.warning("MR не найдены за указанный период")
            return RunAnalysisResponse(
                status="completed",
                fetched_count=0,
                processed_count=0,
                processed_mrs=[],
                message="MR не найдены за указанный период"
            )
        
        logger.success(f"Получено {fetch_result.total_fetched} MR из VCS")
        
        logger.info("[2/2] Обработка MR и расчет метрик...")
        process_command = ProcessMergeRequestsCommand(mrs=fetch_result.mrs)
        process_result = await self._process_uc.invoke(process_command)
        
        logger.success(f"Обработано и сохранено {process_result.total_processed} MR")
        
        logger.info("=" * 60)
        logger.success("Полный анализ успешно завершен!")
        logger.info("=" * 60)
        
        return RunAnalysisResponse(
            status="completed",
            fetched_count=fetch_result.total_fetched,
            processed_count=process_result.total_processed,
            processed_mrs=process_result.processed_mrs,
            message=f"Successfully analyzed {process_result.total_processed} MRs"
        )
