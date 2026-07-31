FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install poetry==1.7.1

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --without dev

COPY . .


EXPOSE 8000

# если миграции и заполнение тестовыми данными на старте не нужны
# нужно закомментировать этот кусок кода ↓
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
#----

# И раскомментировать этот ↓
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]