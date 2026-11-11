FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Pip yangilash
RUN python -m pip install --no-cache-dir --upgrade pip

# Kutubxonalarni o'rnatish
COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

# Root bo'lmagan foydalanuvchi yaratish
RUN addgroup --system app \
    && adduser --system --ingroup app app \
    && mkdir -p /app/staticfiles /app/media /app/celerybeat-data \
    && chown -R app:app /app

COPY --chown=app:app . .

USER app

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
