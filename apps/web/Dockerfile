# syntax=docker/dockerfile:1.7
FROM node:20.18-slim AS dev

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@9.12.0 --activate

# Copy workspace manifests first so `pnpm install` is cached
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml* ./
COPY packages/types/package.json packages/types/
COPY apps/web/package.json apps/web/

RUN pnpm install --frozen-lockfile || pnpm install

# Copy source
COPY packages/types packages/types
COPY apps/web apps/web

WORKDIR /app/apps/web

EXPOSE 5173

CMD ["pnpm", "dev"]