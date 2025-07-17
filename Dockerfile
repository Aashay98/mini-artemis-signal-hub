# ---- Build stage ----
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies (if you need any OS-level ones, add here)
RUN apt-get update && apt-get install -y build-essential gcc && rm -rf /var/lib/apt/lists/*

# Install Python deps into a temp location (for layering)
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --prefix=/install -r requirements.txt

# ---- Runtime stage ----
FROM python:3.11-slim

WORKDIR /app

# Copy only needed files and installed Python packages
COPY --from=builder /install /usr/local
COPY . /app

# Set environment variables for production (can be extended with .env or secrets)
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose port for FastAPI
EXPOSE 8000

# Default command can be overwritten in docker-compose
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
