FROM python:3.11-slim

WORKDIR /app

# Chromium system dependencies — instaladas manualmente (mais leve que --with-deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libnspr4 \
    libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libdbus-1-3 \
    libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libasound2 \
    libpango-1.0-0 libcairo2 \
    libx11-6 libxext6 libx11-xcb1 libxcb1 \
    fonts-liberation fonts-noto-color-emoji \
    wget ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instala só o Chromium (sem baixar o resto)
RUN playwright install chromium

COPY backend/app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
