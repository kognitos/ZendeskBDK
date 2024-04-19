# BDK Runtime Base Image
FROM 719468614044.dkr.ecr.us-west-2.amazonaws.com/kognitos/bdk:1.3.2 as builder

# CodeArtifact Token to download BDK API from
ARG CODE_ARTIFACT_TOKEN

# Set environment variables
ENV POETRY_VERSION=1.8 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1

# Install poetry
RUN python3 -m venv /poetry \
    && /poetry/bin/pip install -U pip setuptools \
    && /poetry/bin/pip install poetry

# Set working directory
WORKDIR /book

# Copy the Python requirements file and install Python dependencies
COPY pyproject.toml poetry.lock /book/

# Install dependencies
RUN /poetry/bin/poetry config http-basic.bdk aws "$CODE_ARTIFACT_TOKEN"\
    && /poetry/bin/poetry config virtualenvs.create false \
    && /poetry/bin/poetry install --only main --no-root \
    && rm -Rf /root/.cache \
    && rm -Rf /root/.config \
    && find /root/.pyenv/versions -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete \
    && find /root/.pyenv/versions -type d -name "test" -exec rm -rf {} + \
    && find /root/.pyenv/versions -type d -name "__pycache__" -exec rm -rf {} +

# Copy project
ADD . ./

# Install the current project
RUN /poetry/bin/poetry build -f wheel -n \
    && pip install --no-deps dist/*.whl

# Final image
FROM 719468614044.dkr.ecr.us-west-2.amazonaws.com/kognitos/bdk:latest

# Copy python environemnt
COPY --from=builder /root/.pyenv/versions /root/.pyenv/versions
