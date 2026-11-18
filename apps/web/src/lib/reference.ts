import { apiRequest } from "./api";
import type { CountrySummary, IndicatorSummary } from "@mil/types";

export const referenceApi = {
  // apiRequest unwraps the `data` field from the envelope automatically.
  // Since the backend returns { data: [...], meta: {...} }, apiRequest returns the array.
  getCountries: (): Promise<CountrySummary[]> =>
    apiRequest<CountrySummary[]>("/countries"),

  getIndicators: (): Promise<IndicatorSummary[]> =>
    apiRequest<IndicatorSummary[]>("/indicators"),
};