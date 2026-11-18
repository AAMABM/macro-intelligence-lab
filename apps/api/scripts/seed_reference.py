"""Seed reference data. Idempotent."""

import asyncio
import sys

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from macro_api.core.db import dispose_engine, get_session_factory
from macro_api.models.reference import (
    Country,
    Currency,
    DataSource,
    Frequency,
    Indicator,
    IndicatorCategory,
    Region,
)

REGIONS = [
    {"code": "GLOBAL", "name": "Global"},
    {"code": "NA", "name": "North America"},
    {"code": "EU", "name": "Europe"},
    {"code": "APAC", "name": "Asia-Pacific"},
]

CURRENCIES = [
    {"code": "USD", "name": "US Dollar", "symbol": "$", "decimals": 2},
    {"code": "EUR", "name": "Euro", "symbol": "€", "decimals": 2},
    {"code": "GBP", "name": "British Pound", "symbol": "£", "decimals": 2},
    {"code": "JPY", "name": "Japanese Yen", "symbol": "¥", "decimals": 0},
    {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥", "decimals": 2},
    {"code": "SGD", "name": "Singapore Dollar", "symbol": "S$", "decimals": 2},
    {"code": "MYR", "name": "Malaysian Ringgit", "symbol": "RM", "decimals": 2},
]

COUNTRIES = [
    {
        "iso2": "US",
        "iso3": "USA",
        "name": "United States",
        "region_code": "NA",
        "currency_code": "USD",
        "flag_emoji": "🇺🇸",
    },
    {
        "iso2": "EU",
        "iso3": "EUR",
        "name": "European Union",
        "region_code": "EU",
        "currency_code": "EUR",
        "flag_emoji": "🇪🇺",
    },
    {
        "iso2": "GB",
        "iso3": "GBR",
        "name": "United Kingdom",
        "region_code": "EU",
        "currency_code": "GBP",
        "flag_emoji": "🇬🇧",
    },
    {
        "iso2": "JP",
        "iso3": "JPN",
        "name": "Japan",
        "region_code": "APAC",
        "currency_code": "JPY",
        "flag_emoji": "🇯🇵",
    },
    {
        "iso2": "CN",
        "iso3": "CHN",
        "name": "China",
        "region_code": "APAC",
        "currency_code": "CNY",
        "flag_emoji": "🇨🇳",
    },
    {
        "iso2": "SG",
        "iso3": "SGP",
        "name": "Singapore",
        "region_code": "APAC",
        "currency_code": "SGD",
        "flag_emoji": "🇸🇬",
    },
    {
        "iso2": "MY",
        "iso3": "MYS",
        "name": "Malaysia",
        "region_code": "APAC",
        "currency_code": "MYR",
        "flag_emoji": "🇲🇾",
    },
]

DATA_SOURCES = [
    {
        "code": "FRED",
        "name": "Federal Reserve Bank of St. Louis",
        "homepage_url": "https://fred.stlouisfed.org",
        "refresh_cadence": "daily",
    },
    {
        "code": "IMF",
        "name": "International Monetary Fund",
        "homepage_url": "https://www.imf.org",
        "refresh_cadence": "quarterly",
    },
    {
        "code": "OECD",
        "name": "Organisation for Economic Co-operation and Development",
        "homepage_url": "https://www.oecd.org",
        "refresh_cadence": "monthly",
    },
    {
        "code": "WB",
        "name": "World Bank",
        "homepage_url": "https://data.worldbank.org",
        "refresh_cadence": "annual",
    },
    {
        "code": "YAHOO",
        "name": "Yahoo Finance",
        "homepage_url": "https://finance.yahoo.com",
        "refresh_cadence": "daily",
    },
    {
        "code": "ALPHAVANTAGE",
        "name": "AlphaVantage",
        "homepage_url": "https://www.alphavantage.co",
        "refresh_cadence": "daily",
    },
    {
        "code": "STOOQ",
        "name": "Stooq",
        "homepage_url": "https://stooq.com",
        "refresh_cadence": "daily",
    },
]

INDICATORS = [
    {
        "code": "GDP_REAL_YOY",
        "name": "Real GDP Growth (YoY)",
        "unit": "%",
        "frequency": Frequency.quarterly,
        "category": IndicatorCategory.growth,
        "source_code": "IMF",
    },
    {
        "code": "CPI_YOY",
        "name": "Consumer Price Index (YoY)",
        "unit": "%",
        "frequency": Frequency.monthly,
        "category": IndicatorCategory.inflation,
        "source_code": "FRED",
    },
    {
        "code": "CORE_CPI_YOY",
        "name": "Core CPI (YoY, ex food & energy)",
        "unit": "%",
        "frequency": Frequency.monthly,
        "category": IndicatorCategory.inflation,
        "source_code": "FRED",
    },
    {
        "code": "POLICY_RATE",
        "name": "Central Bank Policy Rate",
        "unit": "%",
        "frequency": Frequency.monthly,
        "category": IndicatorCategory.rates,
        "source_code": "FRED",
    },
    {
        "code": "UNEMPLOYMENT",
        "name": "Unemployment Rate",
        "unit": "%",
        "frequency": Frequency.monthly,
        "category": IndicatorCategory.labor,
        "source_code": "FRED",
        "higher_is_better": False,
    },
    {
        "code": "PMI_MFG",
        "name": "Manufacturing PMI",
        "unit": "index",
        "frequency": Frequency.monthly,
        "category": IndicatorCategory.survey,
        "source_code": "OECD",
    },
    {
        "code": "CONSUMER_CONFIDENCE",
        "name": "Consumer Confidence Index",
        "unit": "index",
        "frequency": Frequency.monthly,
        "category": IndicatorCategory.survey,
        "source_code": "OECD",
    },
    {
        "code": "INDUSTRIAL_PRODUCTION",
        "name": "Industrial Production (YoY)",
        "unit": "%",
        "frequency": Frequency.monthly,
        "category": IndicatorCategory.growth,
        "source_code": "OECD",
    },
    {
        "code": "TRADE_BALANCE",
        "name": "Trade Balance",
        "unit": "USD bn",
        "frequency": Frequency.monthly,
        "category": IndicatorCategory.external,
        "source_code": "WB",
    },
    {
        "code": "GOV_DEBT_GDP",
        "name": "Government Debt (% of GDP)",
        "unit": "%",
        "frequency": Frequency.annual,
        "category": IndicatorCategory.fiscal,
        "source_code": "IMF",
        "higher_is_better": False,
    },
    {
        "code": "FISCAL_BALANCE_GDP",
        "name": "Fiscal Balance (% of GDP)",
        "unit": "%",
        "frequency": Frequency.annual,
        "category": IndicatorCategory.fiscal,
        "source_code": "IMF",
    },
    {
        "code": "M2_YOY",
        "name": "M2 Money Supply (YoY)",
        "unit": "%",
        "frequency": Frequency.monthly,
        "category": IndicatorCategory.money,
        "source_code": "FRED",
    },
]


async def main() -> int:
    factory = get_session_factory()
    async with factory() as session:
        # Regions
        for r in REGIONS:
            await session.execute(
                insert(Region).values(**r).on_conflict_do_nothing(index_elements=["code"])
            )
        # Currencies
        for c in CURRENCIES:
            await session.execute(
                insert(Currency).values(**c).on_conflict_do_nothing(index_elements=["code"])
            )
        await session.flush()

        regions = {
            row.code: row.id
            for row in (await session.execute(select(Region))).scalars()
        }
        for country in COUNTRIES:
            country_copy = dict(country)
            region_code = country_copy.pop("region_code")
            await session.execute(
                insert(Country)
                .values(region_id=regions.get(region_code), **country_copy)
                .on_conflict_do_nothing(index_elements=["iso2"])
            )
        for s in DATA_SOURCES:
            await session.execute(
                insert(DataSource).values(**s).on_conflict_do_nothing(index_elements=["code"])
            )
        await session.flush()

        sources = {
            row.code: row.id
            for row in (await session.execute(select(DataSource))).scalars()
        }
        for indicator in INDICATORS:
            indicator_copy = dict(indicator)
            source_code = indicator_copy.pop("source_code")
            await session.execute(
                insert(Indicator)
                .values(source_id=sources.get(source_code), **indicator_copy)
                .on_conflict_do_nothing(index_elements=["code"])
            )

        await session.commit()

    await dispose_engine()
    print("Reference data seeded.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
