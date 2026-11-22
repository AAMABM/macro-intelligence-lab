# apps/api/scripts/ingest_markets.py
import asyncio
import sys

import yfinance as yf
from curl_cffi import requests as curl_requests # Use curl_cffi
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from macro_api.core.db import dispose_engine, get_session_factory
from macro_api.models.market import MarketInstrument, MarketPriceDaily

MARKET_SYMBOLS = {
    "^GSPC": {"name": "S&P 500", "class": "equity", "currency": "USD"},
    "GC=F": {"name": "Gold Futures", "class": "commodity", "currency": "USD"},
    "EURUSD=X": {"name": "EUR/USD", "class": "fx", "currency": "USD"},
}


async def main() -> int:
    factory = get_session_factory()
    async with factory() as session:
        # ... (Instrument insertion logic remains the same) ...
        for symbol, meta in MARKET_SYMBOLS.items():
            stmt = (
                insert(MarketInstrument)
                .values(
                    symbol=symbol,
                    name=meta["name"],
                    asset_class=meta["class"],
                    currency_code=meta["currency"],
                )
                .on_conflict_do_nothing(index_elements=["symbol"])
            )
            await session.execute(stmt)
        await session.commit()

        instruments = {
            row.symbol: row
            for row in (await session.execute(select(MarketInstrument))).scalars()
        }

        # Create a session that impersonates Chrome
        chrome_session = curl_requests.Session(impersonate="chrome")

        for symbol, instrument in instruments.items():
            print(f"Fetching market data for {symbol} ({instrument.name})...")
            try:
                df = yf.download(symbol, period="2y", progress=False, session=chrome_session)
            except Exception as e:
                print(f"  -> ERROR downloading {symbol}: {e}")
                continue

            # ... (DataFrame parsing and insertion logic remains the same) ...
            if df.empty:
                print(f"  -> WARNING: Returned no data for {symbol}.")
                continue

            new_rows = 0
            for date_idx, row in df.iterrows():
                price_date = date_idx.date()
                open_p = float(row["Open"].iloc[0]) if hasattr(row["Open"], "iloc") else float(row["Open"])
                high_p = float(row["High"].iloc[0]) if hasattr(row["High"], "iloc") else float(row["High"])
                low_p = float(row["Low"].iloc[0]) if hasattr(row["Low"], "iloc") else float(row["Low"])
                close_p = float(row["Close"].iloc[0]) if hasattr(row["Close"], "iloc") else float(row["Close"])
                vol = int(row["Volume"].iloc[0]) if hasattr(row["Volume"], "iloc") else int(row["Volume"])

                stmt = (
                    insert(MarketPriceDaily)
                    .values(
                        instrument_id=instrument.id,
                        price_date=price_date,
                        open_price=open_p,
                        high_price=high_p,
                        low_price=low_p,
                        close_price=close_p,
                        volume=vol if vol > 0 else None,
                    )
                    .on_conflict_do_nothing(
                        index_elements=["instrument_id", "price_date"]
                    )
                )
                result = await session.execute(stmt)
                if result.rowcount > 0:
                    new_rows += result.rowcount

            print(f"  -> Added {new_rows} new daily prices for {symbol}.")
            await session.commit()

    await dispose_engine()
    print("Market ingestion complete!")
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))