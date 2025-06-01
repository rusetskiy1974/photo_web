FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies for psycopg2 and others
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    build-essential \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv or poetry if needed (optional)
# RUN pip install poetry

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Stage 2: Final image
FROM python:3.12-slim AS runner

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /usr/local /usr/local

# Copy Django project
COPY app app

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=app.settings
ENV PORT=8000

EXPOSE ${PORT}

# Optional: collect static files at runtime
#CMD ["python", "app/manage.py", "collectstatic", "--noinput"]
#RUN python app/manage.py collectstatic --noinput

# Start Gunicorn
CMD ["gunicorn", "--chdir", "app", "--bind", ":8000", "app.wsgi:application"]
#CMD bash -c "python app/manage.py collectstatic --noinput && gunicorn --chdir app --bind :8000 app.wsgi:application"