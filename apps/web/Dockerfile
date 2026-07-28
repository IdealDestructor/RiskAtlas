FROM node:20-alpine AS builder
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@9.12.0 --activate

COPY package.json pnpm-workspace.yaml .npmrc ./
COPY apps/web/package.json ./apps/web/package.json

RUN pnpm install --filter @riskatlas/web

COPY apps/web ./apps/web

ARG NEXT_PUBLIC_API_BASE
ENV NEXT_PUBLIC_API_BASE=$NEXT_PUBLIC_API_BASE
RUN pnpm --filter @riskatlas/web run build

FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
# standalone 模式输出保留 workspace 结构：server.js 在 apps/web/ 下
COPY --from=builder /app/apps/web/.next/standalone ./
# static 资源需放在 server.js 同级的 .next/static 下
COPY --from=builder /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder /app/apps/web/public ./apps/web/public
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
