from dependency_injector.containers import WiringConfiguration, copy

from src.dependency.use_case_container import UseCaseContainer
from src.utils.wiring_modules import find_wiring_modules


@copy(UseCaseContainer)
class Container(UseCaseContainer):
    wiring_config = WiringConfiguration(modules=find_wiring_modules())
