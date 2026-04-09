"""
Application configuration using Pydantic Settings
"""
from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig:
    """Server configuration"""
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port


class VCSProvider(str, Enum):
    GITLAB = "gitlab"
    GITHUB = "github"


class AppConfig(BaseSettings):
    """Main application configuration"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # VCS Configuration
    vcs_provider: VCSProvider = Field(default=VCSProvider.GITLAB)
    gitlab_token: str | None = Field(default=None, alias="GITLAB_TOKEN")
    gitlab_url: str = Field(default="https://gitlab.com", alias="GITLAB_URL")
    project_id: int | None = Field(default=None, alias="PROJECT_ID")
    
    github_token: str | None = Field(default=None, alias="GITHUB_TOKEN")
    github_repo: str | None = Field(default=None, alias="GITHUB_REPO")
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql://localhost:5432/mr_analytics",
        alias="DATABASE_URL"
    )
    
    @property
    def is_postgres(self) -> bool:
        """Check if using PostgreSQL"""
        return self.database_url.startswith("postgresql")
    
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite"""
        return self.database_url.startswith("sqlite")
    
    # Analytics
    days_to_analyze: int = Field(default=30, alias="DAYS_TO_ANALYZE")
    
    # API Settings
    api_timeout: int = Field(default=30, alias="API_TIMEOUT")
    api_per_page: int = Field(default=20, alias="API_PER_PAGE")
    
    # Server Configuration
    server_host: str = Field(default="0.0.0.0", alias="SERVER_HOST")
    server_port: int = Field(default=8000, alias="SERVER_PORT")
    
    # Documentation
    enable_docs: bool = Field(default=True, alias="ENABLE_DOCS")
    
    @property
    def server(self):
        """Server configuration object"""
        return ServerConfig(host=self.server_host, port=self.server_port)
    
    @property
    def token(self) -> str:
        """Get token based on provider"""
        if self.vcs_provider == VCSProvider.GITLAB:
            return self.gitlab_token
        return self.github_token
    
    @property
    def base_url(self) -> str:
        """Get base URL based on provider"""
        if self.vcs_provider == VCSProvider.GITLAB:
            return self.gitlab_url
        return "https://api.github.com"
    
    @property
    def project_id_value(self) -> str:
        """Get project_id as string for GitLab API"""
        if self.project_id is None:
            return "None"
        return str(self.project_id)


settings = AppConfig()
