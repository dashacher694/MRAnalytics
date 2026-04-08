"""
Base containers for dependency injection.

This module provides base containers for managing dependencies,
including configurations, database, VCS clients and other core services.
"""

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton

from src.core.config import settings
from src.db.connection import engine
from src.infrastructure.clients.gitlab import GitLabClient
from src.infrastructure.clients.github import GitHubClient


class BaseContainer(DeclarativeContainer):
    """
    Base dependency container.
    
    This container provides all necessary dependencies for the application,
    including configurations, database, VCS clients and other core services.
    """
    
    config = Configuration()
    config.from_dict(settings.model_dump())
    
    db_engine = Singleton(lambda: engine)
    
    # GitLab client
    gitlab_client = Singleton(
        GitLabClient,
        token=settings.token,
        base_url=settings.base_url,
        project_id=settings.project_id or 0,
        timeout=settings.api_timeout,
    )
    
    # GitHub client
    github_client = Singleton(
        GitHubClient,
        token=settings.github_token,
        repo=settings.github_repo,
        timeout=settings.api_timeout,
    )
    
    # Dynamic VCS client based on provider
    vcs_client = Singleton(
        github_client if settings.vcs_provider.value == "github" else gitlab_client
    )
