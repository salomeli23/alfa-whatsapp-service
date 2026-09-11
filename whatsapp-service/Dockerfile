FROM node:20-slim
# git + ca-certificates son necesarios porque Baileys instala una dependencia por git
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY package.json yarn.lock* ./
RUN yarn install --production --frozen-lockfile || yarn install --production
COPY index.js ./
ENV PORT=3001
EXPOSE 3001
CMD ["node", "index.js"]
