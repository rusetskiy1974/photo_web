FROM python:3.12.7

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt update -y && \
    apt install -y python3-dev \
    gcc \
    musl-dev

COPY pyproject.toml .

RUN pip install --upgrade pip
RUN pip install poetry

RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi

# Set Django settings module for commands
ENV DJANGO_SETTINGS_MODULE=app.settings

COPY app .

#RUN python manage.py collectstatic #--noinput    # --settings=app.settings

EXPOSE 8000
CMD gunicorn --chdir app --bind 0.0.0.0:8000 app.wsgi:application