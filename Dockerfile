FROM python:3.12-slim-bookworm@sha256:e697c81897302a4c4333bade000d98038fbb21eb064f8ee1fd42d02ebcd9d337

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements-runtime.lock ./requirements-runtime.lock
RUN python -m pip install --no-cache-dir --require-hashes -r requirements-runtime.lock \
    && printf '%s\\n' 'setuptools==78.1.1 --hash=sha256:c3a9c4211ff4c309edb8b8c4f1cbfa7ae324c4ba9f91ff254e3d305b9fd54561' > /tmp/setuptools.lock \
    && python -m pip install --no-cache-dir --no-deps --require-hashes -r /tmp/setuptools.lock \
    && rm /tmp/setuptools.lock \
    && groupadd --gid 10001 atlas \
    && useradd --uid 10001 --gid 10001 --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin atlas

COPY api ./api
COPY data/study_area_register.json ./data/study_area_register.json
COPY data/study_area_evidence.json ./data/study_area_evidence.json
USER 10001:10001
EXPOSE 8080
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
