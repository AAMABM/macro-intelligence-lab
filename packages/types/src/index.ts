/**
 * Macro Intelligence Lab — Shared Types
 */

export interface Meta {
  requestId: string;
  asOf: string;
  nextCursor?: string | null;
  total?: number | null;
}

export interface Page<T> {
  data: T[];
  meta: Meta;
}

export interface Envelope<T> {
  data: T;
  meta: Meta;
}

export interface CountrySummary {
  id: number;
  iso2: string;
  iso3: string;
  name: string;
  flagEmoji: string | null;
  regionCode: string | null;
  currencyCode: string | null;
}

export interface IndicatorSummary {
  id: number;
  code: string;
  name: string;
  unit: string | null;
  frequency: string;
  category: string;
}

export interface ObservationPoint {
  period: string;
  value: string;
}

export interface SeriesResponse {
  indicatorCode: string;
  countryIso2: string;
  points: ObservationPoint[];
}

export interface CountryDetail {
  id: number;
  iso2: string;
  iso3: string;
  name: string;
  flagEmoji: string | null;
  regionCode: string | null;
  regionName: string | null;
  currencyCode: string | null;
  currencyName: string | null;
  isActive: boolean;
}

export interface MarketInstrumentSummary {
  id: number;
  symbol: string;
  name: string;
  assetClass: string;
  currencyCode: string | null;
}

export interface MarketPricePoint {
  priceDate: string;
  closePrice: string;
}

export interface MarketSeriesResponse {
  symbol: string;
  name: string;
  points: MarketPricePoint[];
}