FROM python:3.13-slim AS base

WORKDIR /app

ENV PYTHONPATH=/app/django_app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv pip install --system --no-cache .

COPY . .


FROM base AS dev

RUN uv export --frozen --all-groups --no-hashes -o /tmp/requirements-dev.txt && \
    uv pip install --system --no-cache -r /tmp/requirements-dev.txt

RUN sed -i 's/\r//' entrypoint.sh && chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]


FROM base AS web

RUN sed -i 's/\r//' entrypoint.sh && chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]


FROM base AS test

RUN uv export --frozen --all-groups --no-hashes -o /tmp/requirements-dev.txt && \
    uv pip install --system --no-cache -r /tmp/requirements-dev.txt

RUN printf '#!/bin/sh\nset -e\npytest -v\n' > /usr/local/bin/run-tests \
    && chmod +x /usr/local/bin/run-tests
