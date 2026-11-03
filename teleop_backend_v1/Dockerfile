FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Development only: apply Django's built-in migrations, then enable auto-reload.
CMD ["sh", "-c", "python manage.py migrate --noinput && exec python manage.py runserver 0.0.0.0:8000"]
