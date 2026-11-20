import { apiRequest } from "./api";
import type { CountrySummary, IndicatorSummary, SeriesResponse } from "@mil/types";

export const referenceApi = {
  getCountries: (): Promise<CountrySummary[]> =>
    apiRequest<CountrySummary[]>("/countries"),

  getIndicators: (): Promise<IndicatorSummary[]> =>
    apiRequest<IndicatorSummary[]>("/indicators"),

  // Add this new function:
  getSeries: (code: string, country: string = "US"): Promise<SeriesResponse> =>
    apiRequest<SeriesResponse>(`/indicators/${code}/series?country=${country}`),
};