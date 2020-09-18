FROM python:3.8.5-buster
RUN apt-get update
ENV PYTHONPATH="/app" \
  PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=on \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  POETRY_VERSION=1.0.10 \
  POETRY_VIRTUALENVS_CREATE=false \
  PATH="${PATH}:/root/.poetry/bin"

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
RUN poetry install --no-dev
COPY covid_stats ./covid_stats
EXPOSE "${PROMETHEUS_APP_PORT}/tcp"
ENTRYPOINT ["python","./covid_stats/main.py"]

