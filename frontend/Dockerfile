# Desarrollo: Node + pnpm; el código se monta con volumen.
FROM node:24-bookworm-slim

ENV PNPM_HOME=/pnpm
ENV PATH=$PNPM_HOME:$PATH

RUN corepack enable

WORKDIR /app

EXPOSE 5173

CMD ["pnpm", "dev", "--host", "0.0.0.0"]
