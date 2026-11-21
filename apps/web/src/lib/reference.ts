import { apiRequest } from "./api";
import type { CountrySummary, IndicatorSummary, SeriesResponse, CountryDetail } from "@mil/types";

export const referenceApi = {
  // ... keep the existing ones ...
  getCountries: (): Promise<CountrySummary[]> => apiRequest<CountrySummary[]>("/countries"),
  getIndicators: (): Promise<IndicatorSummary[]> => apiRequest<IndicatorSummary[]>("/indicators"),
  getSeries: (code: string, country: string = "US"): Promise<SeriesResponse> => apiRequest<SeriesResponse>(`/indicators/${code}/series?country=${country}`),

  // Add this:
  getCountryDetail: (iso2: string): Promise<CountryDetail> =>
    apiRequest<CountryDetail>(`/countries/${iso2}`),
};