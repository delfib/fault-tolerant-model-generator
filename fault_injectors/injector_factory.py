from fault_injectors.stuck_at_injector import StuckAtInjector
from fault_injectors.byzantine_injector import ByzantineInjector

def create_injector(faults):
    if not faults:
        raise ValueError("Factory Generation Error: No faults provided.")

    fault_type = faults[0].type.strip().lower()

    if fault_type == "stuck-at":
        return StuckAtInjector(faults)

    if fault_type == "byzantine":
        return ByzantineInjector(faults)

    raise ValueError(f"Factory Generation Error: Unsupported fault type '{fault_type}'")