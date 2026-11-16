"""Reference data tests."""

import pytest
from sqlalchemy import text

from macro_api.core.db import get_session_factory


@pytest.mark.asyncio
async def test_seed_creates_regions_and_countries() -> None:
    """After the seed script has been run, the reference tables have data."""
    factory = get_session_factory()
    async with factory() as session:
        regions = await session.scalar(text("SELECT count(*) FROM regions"))
        countries = await session.scalar(text("SELECT count(*) FROM countries"))
        indicators = await session.scalar(text("SELECT count(*) FROM indicators"))

    # If the seed script has NOT been run, these will be 0. The test skips
    # rather than fails in that case, since seeding is an explicit operator
    # step (see scripts/seed_reference.py).
    if regions == 0 or countries == 0 or indicators == 0:
        pytest.skip("Reference data not seeded; run scripts/seed_reference.py")

    assert regions >= 4
    assert countries >= 7
    assert indicators >= 12
