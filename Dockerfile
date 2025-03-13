FROM python:3.13-alpine

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_CREATE=false 

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps \
    gcc musl-dev libffi-dev openssl-dev && \
    apk add --no-cache bash curl && \
    python -m ensurepip --upgrade && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps

COPY flemmarr/ .

ENTRYPOINT ["python"]

CMD ["setup.py"]
