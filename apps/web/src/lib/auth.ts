import { apiRequest } from "./api";

export type UserRole = "guest" | "research_user" | "admin";
export type UserStatus = "active" | "suspended" | "deleted";

export interface UserDetail {
  id: string;
  email: string;
  displayName: string;
  role: UserRole;
  status: UserStatus;
  avatarUrl?: string | null;
  bio?: string | null;
  emailVerifiedAt?: string | null;
  lastLoginAt?: string | null;
  createdAt: string;
}

export interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  accessExpiresAt: string;
  user: UserDetail;
}

export interface RegisterPayload {
  email: string;
  password: string;
  displayName: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export const authApi = {
  register: (payload: RegisterPayload): Promise<AuthResponse> =>
    apiRequest<AuthResponse>("/auth/register", { method: "POST", body: payload }),

  login: (payload: LoginPayload): Promise<AuthResponse> =>
    apiRequest<AuthResponse>("/auth/login", { method: "POST", body: payload }),

  refresh: (refreshToken: string): Promise<AuthResponse> =>
    apiRequest<AuthResponse>("/auth/refresh", {
      method: "POST",
      body: { refreshToken },
    }),

  logout: (refreshToken: string): Promise<void> =>
    apiRequest<void>("/auth/logout", {
      method: "POST",
      body: { refreshToken },
    }),

  me: (accessToken: string): Promise<UserDetail> =>
    apiRequest<UserDetail>("/users/me", { accessToken }),
};