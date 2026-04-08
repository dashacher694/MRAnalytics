"""
Application entry point
"""
from src.core.config import settings

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.application:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=True,
    )
