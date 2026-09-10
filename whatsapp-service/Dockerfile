FROM node:20-slim
WORKDIR /app
COPY package.json ./
RUN yarn install --production
COPY index.js ./
ENV PORT=3001
EXPOSE 3001
CMD ["node", "index.js"]
