FROM python:3.11

WORKDIR /app/

# Install Poetry
RUN pip install poetry

RUN poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY pyproject.toml ./app/poetry.lock* /app/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

ENV C_FORCE_ROOT=1

COPY . /

RUN chmod +x /worker-start.sh

WORKDIR /

CMD ["bash", "/worker-start.sh"]
