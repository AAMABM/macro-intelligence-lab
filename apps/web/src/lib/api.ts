/**
 * API client.
 *
 * All requests go through this wrapper so:
 * - The envelope is unwrapped consistently (data, not envelope).
 * - Errors have a stable shape (`ApiError`).
 * - Auth header injection is a single point of change.
 */

export class ApiError extends Error {
  code: string;
  status: number;
  details: Record<string, unknown>;
  requestId: string | null;

  constructor(init: {
    code: string;
    message: string;
    status: number;
    details?: Record<string, unknown>;
    requestId?: string | null;
  }) {
    super(init.message);
    this.name = "ApiError";
    this.code = init.code;
    this.status = init.status;
    this.details = init.details ?? {};
    this.requestId = init.requestId ?? null;
  }
}

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

type Envelope<T> = {
  data: T;
  meta: { requestId: string; asOf: string };
};

type RequestOptions = {
  method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  body?: unknown;
  accessToken?: string | null;
  signal?: AbortSignal;
};

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (options.body !== undefined) headers["Content-Type"] = "application/json";
  if (options.accessToken) headers["Authorization"] = `Bearer ${options.accessToken}`;

  const response = await fetch(`${API_URL}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    signal: options.signal,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const text = await response.text();
  const json = text ? JSON.parse(text) : {};

  if (!response.ok) {
    const err = json?.error ?? {};
    throw new ApiError({
      code: err.code ?? "unknown_error",
      message: err.message ?? "Request failed.",
      status: response.status,
      details: err.details,
      requestId: err.requestId ?? response.headers.get("X-Request-ID"),
    });
  }

  return (json as Envelope<T>).data;
}