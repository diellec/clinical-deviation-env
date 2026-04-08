FROM python:3.11-slim

WORKDIR /app

# Install system deps (safe guard)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

EXPOSE 7860

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "7860"]