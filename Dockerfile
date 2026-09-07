FROM node:22-alpine AS frontend
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY index.html tsconfig.json vite.config.ts ./
COPY src ./src
COPY public ./public
RUN npm run build

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home --uid 10001 changeguard
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr && rm -rf /var/lib/apt/lists/*
COPY backend ./backend
COPY industry_packs ./industry_packs
COPY rules ./rules
COPY domain_packs ./domain_packs
COPY migrations ./migrations
COPY alembic.ini ./
COPY scripts ./scripts
COPY samples ./samples
COPY --from=frontend /app/dist ./dist
RUN mkdir -p /app/data/documents && chown -R changeguard:changeguard /app/data
USER changeguard
EXPOSE 8000
CMD ["uvicorn","backend.main:app","--host","0.0.0.0","--port","8000","--no-access-log"]
