"""Fetch economic data from FRED and load into the database."""

import asyncio
import os
import sys
from datetime import datetime

import httpx
from sqlalchemy import select, update

from macro_api.core.db import dispose_engine, get_session_factory
from macro_api.models.macro import IndicatorObservation
from macro_api.models.reference import Country, DataSource, Indicator

# Map our internal indicator codes to FRED series IDs
FRED_SERIES = {
    "CPI_YOY": "CPIAUCSL",       # Consumer Price Index
    "GDP_REAL_YOY": "GDPC1",     # Real GDP
    "UNEMPLOYMENT": "UNRATE",    # Unemployment Rate
}


async def fetch_fred_data(series_id: str, api_key: str) -> list[dict]:
    """Fetch observations from FRED API."""
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": "2015-01-01",  # Fetch the last ~10 years
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json().get("observations", [])


async def main() -> int:
    api_key = os.environ.get("MIL_FRED_API_KEY")
    if not api_key or api_key == "paste_your_32_character_key_here":
        print("ERROR: MIL_FRED_API_KEY is not set.", file=sys.stderr)
        return 1

    factory = get_session_factory()
    async with factory() as session:
        # 1. Get US country ID and FRED source ID
        us_country = await session.scalar(select(Country).where(Country.iso2 == "US"))
        fred_source = await session.scalar(select(DataSource).where(DataSource.code == "FRED"))
        
        if not us_country or not fred_source:
            print("ERROR: Reference data (US country, FRED source) not found. Run seed_reference.py first.", file=sys.stderr)
            return 1

        # 2. Loop through our target indicators
        for indicator_code, fred_id in FRED_SERIES.items():
            indicator = await session.scalar(select(Indicator).where(Indicator.code == indicator_code))
            if not indicator:
                print(f"WARNING: Indicator {indicator_code} not found in DB. Skipping.")
                continue

            print(f"Fetching {indicator_code} ({fred_id}) from FRED...")
            observations = await fetch_fred_data(fred_id, api_key)
            
            # 3. Insert into the DB with vintage handling
            new_rows = 0
            for obs in observations:
                val_str = obs["value"]
                if val_str == ".":  # FRED uses "." for missing data
                    continue

                period_date = datetime.strptime(obs["date"], "%Y-%m-%d").date()
                value = float(val_str)

                # Check if this observation already exists as the latest
                existing = await session.scalar(
                    select(IndicatorObservation).where(
                        IndicatorObservation.indicator_id == indicator.id,
                        IndicatorObservation.country_id == us_country.id,
                        IndicatorObservation.period == period_date,
                        IndicatorObservation.is_latest == True
                    )
                )

                if existing:
                    # If it exists and the value hasn't changed, do nothing
                    if float(existing.value) == value:
                        continue
                    
                    # If it changed (revision), mark the old one as not latest
                    existing.is_latest = False
                    revision_num = existing.revision + 1
                else:
                    revision_num = 0

                # Insert the new observation
                new_obs = IndicatorObservation(
                    indicator_id=indicator.id,
                    country_id=us_country.id,
                    period=period_date,
                    value=value,
                    revision=revision_num,
                    is_latest=True,
                    source_id=fred_source.id,
                    source_ts=datetime.utcnow(),
                )
                session.add(new_obs)
                new_rows += 1

            print(f"  -> Added {new_rows} new observations for {indicator_code}.")

        await session.commit()
        print("Ingestion complete!")

    await dispose_engine()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))