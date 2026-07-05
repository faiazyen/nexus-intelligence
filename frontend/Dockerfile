# syntax=docker/dockerfile:1
# NEXUS Intelligence frontend — Next.js 14 (App Router) on node:20-alpine
#
# REQUIREMENT: next.config.mjs must set `output: "standalone"` (owned by the
# frontend workstream). The runner stage below copies the standalone server
# bundle; without that setting the final stage will fail to build.

# ---------- Stage 1: dependencies ----------
FROM node:20-alpine AS deps

WORKDIR /app

COPY package.json package-lock.json* ./
# npm ci when a lockfile is committed; npm install as a bootstrap fallback
# while the frontend workstream is still generating the lockfile.
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# ---------- Stage 2: build ----------
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# NEXT_PUBLIC_* vars are inlined into the client bundle at build time.
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_TELEMETRY_DISABLED=1

# Guarantee public/ exists so the runner COPY never fails.
RUN mkdir -p public && npm run build

# ---------- Stage 3: runner ----------
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
