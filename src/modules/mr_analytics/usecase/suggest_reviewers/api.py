import uuid
from fastapi import APIRouter, Depends, Path
from dependency_injector.wiring import Provide, inject
from starlette import status
from loguru import logger

from src.core.containers import Container
from src.modules.mr_analytics.usecase.suggest_reviewers.impl import SuggestReviewersUseCase
from src.modules.mr_analytics.usecase.suggest_reviewers.command import SuggestReviewersRequest

router = APIRouter()


@router.post(
    "/suggest-reviewers",
    name="Suggest Reviewers",
    summary="Предлагает ревьюеров для Merge Request",
    status_code=status.HTTP_200_OK,
)
@inject
async def suggest_reviewers(
    request: SuggestReviewersRequest,
    uc: SuggestReviewersUseCase = Depends(Provide[Container.suggest_reviewers_usecase]),
):
    """
    # Предлагает ревьюеров для Merge Request.

    Метод для получения предложений ревьюеров на основе анализа MR.

    ___

    #### Успешный ответ:
    Отдает 200 со списком предложенных ревьюеров

    #### Ошибки:
    - 400 Bad Request: Некорректный запрос или неверный формат данных.
    - 404 Not Found: MR с указанным IID не найден.
    - 500 Internal Server Error: Внутренняя ошибка сервера.
    """
    
    logger.info(f"API: Suggesting reviewers for MR !{request.mr_iid}")
    
    result = await uc.invoke(request)
    return result
