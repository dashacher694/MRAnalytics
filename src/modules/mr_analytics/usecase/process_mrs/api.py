import uuid
from fastapi import APIRouter, Depends, Path
from dependency_injector.wiring import Provide, inject
from starlette import status
from loguru import logger

from src.dependency.container import Container
router = APIRouter()
from src.modules.mr_analytics.usecase.process_mrs.impl import ProcessMergeRequestsUseCase
from src.modules.mr_analytics.usecase.process_mrs.command import ProcessMergeRequestsCommand


@router.post(
    "/process-mrs",
    name="Process Merge Requests",
    summary="Обрабатывает Merge Requests",
    status_code=status.HTTP_200_OK,
)
@inject
async def process_mrs(
    command: ProcessMergeRequestsCommand,
    uc: ProcessMergeRequestsUseCase = Depends(Provide[Container.process_mrs_usecase]),
):
    """
    # Обрабатывает Merge Requests.

    Метод для обработки VCS Merge Request и расчета метрик.

    ___

    #### Успешный ответ:
    Отдает 200 с результатами обработки MR

    #### Ошибки:
    - 400 Bad Request: Некорректный запрос или неверный формат данных.
    - 500 Internal Server Error: Внутренняя ошибка сервера.
    """
    
    logger.info(f"API: Processing {len(command.mrs)} MRs")
    
    result = await uc.invoke(command)
    return result
