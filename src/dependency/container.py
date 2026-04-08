"""
Main dependency injection container.

This module provides the main Container that combines all other containers
and configures wiring for automatic dependency injection.
"""

from dependency_injector.containers import WiringConfiguration, copy

from src.dependency.use_case_container import UseCaseContainer
from src.utils.wiring_modules import find_wiring_modules


@copy(UseCaseContainer)
class Container(UseCaseContainer):
    """
    Main application container that inherits from UseCaseContainer
    and configures automatic wiring for dependency injection.
    """
    wiring_config = WiringConfiguration(modules=find_wiring_modules())
