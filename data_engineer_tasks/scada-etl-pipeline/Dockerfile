FROM apache/airflow:2.10.2-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow
COPY requirements.txt /opt/airflow/requirements.txt

# apache-airflow is already in the base image; installing it again from
# requirements.txt would fight the base image's pinned constraints, so we
# strip it out here and install everything else.
#
# sqlalchemy is also excluded: the base image ships sqlalchemy==1.4.54,
# which Airflow's own ORM models (e.g. TaskInstance) require. Force-installing
# the pipeline's sqlalchemy==2.0.35 into this same environment upgrades it
# out from under Airflow and breaks the scheduler/webserver at import time.
# alembic and psycopg2-binary both work fine against the base image's 1.4.x.
RUN grep -vE '^(apache-airflow|sqlalchemy)==' /opt/airflow/requirements.txt > /opt/airflow/requirements.pipeline.txt \
    && pip install --no-cache-dir -r /opt/airflow/requirements.pipeline.txt

COPY src/ /opt/airflow/src/
COPY alembic.ini /opt/airflow/alembic.ini
COPY migrations/ /opt/airflow/migrations/
