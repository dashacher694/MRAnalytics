"""
Главный скрипт: запускает весь пайплайн
"""
import asyncio
import sys

from loguru import logger

from src.core.logging import setup_logging
from src.core.containers import Container
from src.core.config import settings
from src.core.errors import MRAnalyticsException
from src.db.connection import init_db


async def main():
    """Main pipeline execution"""
    setup_logging()
    
    logger.info("=" * 60)
    logger.info("MR Analytics Pipeline")
    logger.info("=" * 60)
    
    container = Container()
    
    try:
        logger.info("[0/2] Initializing database")
        await init_db()
        
        logger.info(f"[1/2] Fetching MRs from {settings.vcs_provider.value}")
        fetch_usecase = container.fetch_mrs_usecase()
        mrs = await fetch_usecase.execute(days=settings.days_to_analyze)
        
        if not mrs:
            logger.error("No MRs found. Check your configuration.")
            sys.exit(1)
        
        logger.info("[2/2] Calculating metrics and saving to database")
        async with container.uow() as uow:
            calc_usecase = container.calculate_metrics_usecase()
            calc_usecase.uow = uow
            metrics = await calc_usecase.execute(mrs)
        
        logger.success("=" * 60)
        logger.success("✅ Pipeline completed successfully!")
        logger.success(f"Processed {len(metrics)} MRs")
        logger.success("Run dashboard: streamlit run dashboard.py")
        logger.success("=" * 60)
        
    except MRAnalyticsException as e:
        logger.error(f"❌ Application error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
