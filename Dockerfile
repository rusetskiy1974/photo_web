# Stage 1: Build dependencies
FROM python:3-alpine AS builder

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev

# Create virtual environment
RUN python3 -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Stage 2: Final image
FROM python:3-alpine AS runner

WORKDIR /app

# Install system dependencies (needed by Python packages)
RUN apk add --no-cache libffi

# Copy virtual environment from builder
COPY --from=builder /app/venv venv

# Copy Django project
COPY app app

# Set environment variables
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE=app.settings
ENV PORT=8000

EXPOSE ${PORT}

# Collect static files at runtime (optional)
CMD ["python", "app/manage.py", "collectstatic", "--noinput"]

# Start Gunicorn
CMD ["gunicorn", "--chdir", "app", "--bind", ":8000", "app.wsgi:application"]