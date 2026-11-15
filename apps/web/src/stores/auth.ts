import { create } from "zustand";
import { ApiError } from "@/lib/api";
import { authApi, type UserDetail } from "@/lib/auth";

type AuthStatus = "idle" | "loading" | "authenticated" | "unauthenticated";

interface AuthState {
  user: UserDetail | null;
  accessToken: string | null;
  status: AuthStatus;
  error: string | null;

  initialize: () => Promise<void>;
  register: (email: string, password: string, displayName: string) => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

const REFRESH_KEY = "mil.refresh";

function readRefresh(): string | null {
  try {
    return localStorage.getItem(REFRESH_KEY);
  } catch {
    return null;
  }
}

function writeRefresh(token: string | null): void {
  try {
    if (token) localStorage.setItem(REFRESH_KEY, token);
    else localStorage.removeItem(REFRESH_KEY);
  } catch {
    /* ignore quota / private-mode errors */
  }
}

function extractError(err: unknown): string {
  if (err instanceof ApiError) return err.message;
  if (err instanceof Error) return err.message;
  return "Something went wrong.";
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: null,
  status: "idle",
  error: null,

    initialize: async () => {
    // Guard against StrictMode double-invoke and any accidental re-trigger.
    // `status` starts as "idle"; the first call flips it to "loading" (or
    // "unauthenticated" if no token) synchronously, so any subsequent call
    // short-circuits here.
    if (get().status !== "idle") return;

    const refreshToken = readRefresh();
    if (!refreshToken) {
      set({ status: "unauthenticated" });
      return;
    }
    set({ status: "loading" });
    try {
      const response = await authApi.refresh(refreshToken);
      writeRefresh(response.refreshToken);
      set({
        user: response.user,
        accessToken: response.accessToken,
        status: "authenticated",
        error: null,
      });
    } catch {
      writeRefresh(null);
      set({
        user: null,
        accessToken: null,
        status: "unauthenticated",
        error: null,
      });
    }
  },

  register: async (email, password, displayName) => {
    set({ status: "loading", error: null });
    try {
      const response = await authApi.register({ email, password, displayName });
      writeRefresh(response.refreshToken);
      set({
        user: response.user,
        accessToken: response.accessToken,
        status: "authenticated",
      });
    } catch (err) {
      set({ status: "unauthenticated", error: extractError(err) });
      throw err;
    }
  },

  login: async (email, password) => {
    set({ status: "loading", error: null });
    try {
      const response = await authApi.login({ email, password });
      writeRefresh(response.refreshToken);
      set({
        user: response.user,
        accessToken: response.accessToken,
        status: "authenticated",
      });
    } catch (err) {
      set({ status: "unauthenticated", error: extractError(err) });
      throw err;
    }
  },

  logout: async () => {
    const refresh = readRefresh();
    if (refresh) {
      try {
        await authApi.logout(refresh);
      } catch {
        /* already revoked / expired — safe to ignore */
      }
    }
    writeRefresh(null);
    set({
      user: null,
      accessToken: null,
      status: "unauthenticated",
      error: null,
    });
  },

  clearError: () => {
    if (get().error !== null) set({ error: null });
  },
}));