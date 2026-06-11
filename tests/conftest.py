"""
Shared pytest configuration and fixtures.

This conftest.py is loaded automatically for all tests under tests/.
It provides:

1. Autouse session-scoped setup that clears strategy-research modules from sys.modules
   after the full collection phase, so import-isolation tests (test_no_strategy_logic_import,
   test_observation_cycle_not_invoked_via_import) pass regardless of test ordering.

2. No production data is created or mutated here.
"""
import sys
import pytest


# Modules that import-isolation tests verify are NOT loaded by reporting modules.
# When the full suite runs, earlier test files load these as a side effect.
# They must be purged before the isolation tests run.
_STRATEGY_MODULE_PREFIXES = (
    "src.research.momentum",
    "src.research.price_volume",
    "src.paper.observation_cycle",
    "src.paper.relative_strength_observation_cycle",
)


def _purge_strategy_modules() -> list[str]:
    """Remove strategy/observation-cycle modules from sys.modules. Returns removed list."""
    to_remove = [
        key for key in list(sys.modules.keys())
        if any(key.startswith(p) for p in _STRATEGY_MODULE_PREFIXES)
    ]
    for key in to_remove:
        del sys.modules[key]
    return to_remove


@pytest.fixture(autouse=True)
def _auto_isolate_strategy_imports(request):
    """
    Autouse function-scoped fixture.

    For import-isolation tests (test_no_strategy_logic_import,
    test_observation_cycle_not_invoked_via_import), purges strategy/
    observation-cycle src modules from sys.modules before the test runs.
    This ensures the check sees a clean slate regardless of which other
    modules ran earlier in the session.

    Only fires for the specific isolation tests — lightweight, no-op otherwise.
    Safe: only removes optional side-effect imports, never mutates files or data.
    """
    isolation_test_names = {
        "test_no_strategy_logic_import",
        "test_observation_cycle_not_invoked_via_import",
    }
    if request.node.name in isolation_test_names:
        _purge_strategy_modules()
    yield
