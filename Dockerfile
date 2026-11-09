FROM python:3.12-alpine@sha256:e6dae589c1c05976188fd3bd019afd091445fc533ed2ea29001beddc7368a9c8 AS dependencies

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
COPY requirements-runtime.lock ./requirements-runtime.lock
RUN python -m pip install --no-cache-dir --require-hashes --target=/opt/atlas-python -r requirements-runtime.lock \
    && rm -rf /opt/atlas-python/pip /opt/atlas-python/pip-*.dist-info

FROM python:3.12-alpine@sha256:e6dae589c1c05976188fd3bd019afd091445fc533ed2ea29001beddc7368a9c8

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY --from=dependencies /opt/atlas-python /usr/local/lib/python3.12/site-packages
RUN addgroup -g 10001 -S atlas \
    && adduser -u 10001 -S -G atlas -H -D -s /sbin/nologin atlas

COPY api ./api
COPY data/study_area_register.json ./data/study_area_register.json
COPY data/study_area_evidence.json ./data/study_area_evidence.json
USER 10001:10001
EXPOSE 8080
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
