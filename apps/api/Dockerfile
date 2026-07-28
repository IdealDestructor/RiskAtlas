FROM python:3.12-slim AS builder

WORKDIR /build
RUN pip install --no-cache-dir uv==0.5.4

COPY apps/api/pyproject.toml ./
RUN uv pip install --no-cache-dir --system --compile .

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY apps/api/app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
