FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system packages + Chrome + chromedriver
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    build-essential \
    libnss3 \
    libgconf-2-4 \
    libxi6 \
    libxcursor1 \
    libxrandr2 \
    libxcomposite1 \
    libasound2 \
    libxdamage1 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgbm-dev \
    libxss1 \
    fonts-liberation \
    libappindicator1 \
    xdg-utils \
    default-libmysqlclient-dev \
    pkg-config \
    chromium \
    chromium-driver \
    && apt-get clean

# Set path for chromedriver
ENV PATH="/usr/lib/chromium/:${PATH}"

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
