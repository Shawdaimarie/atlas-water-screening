FROM python:3.12-slim-trixie@sha256:b18b261e1b4974b4f321451ad5251ded85abb22c2b8b262da527dda1d031ab30

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements-runtime.lock ./requirements-runtime.lock
RUN python -m pip install --no-cache-dir --require-hashes -r requirements-runtime.lock \
    && groupadd --gid 10001 atlas \
    && useradd --uid 10001 --gid 10001 --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin atlas

COPY api ./api
COPY data/study_area_register.json ./data/study_area_register.json
COPY data/study_area_evidence.json ./data/study_area_evidence.json
USER 10001:10001
EXPOSE 8080
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
