from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton

from src.core.config import settings
from src.db.connection import engine
from src.infrastructure.clients.gitlab import GitLabClient


class BaseContainer(DeclarativeContainer):
    
    config = Configuration()
    config.from_dict(settings.model_dump())
    
    db_engine = Singleton(lambda: engine)
    
    vcs_client = Singleton(
        GitLabClient,
        token=settings.token,
        base_url=settings.base_url,
        project_id=settings.project_id,
        timeout=settings.api_timeout,
    )
