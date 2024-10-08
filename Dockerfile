# BDK Runtime Version
ARG BDK_RUNTIME_IMAGE_URI="719468614044.dkr.ecr.us-west-2.amazonaws.com/kognitos/bdk:latest"

# BDK Runtime Base Image
FROM ${BDK_RUNTIME_IMAGE_URI} as builder

# Set environment variables
ENV POETRY_VERSION=1.8 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1

# Find utils don't come pre-installed on Amazon Linux 2023 which is the base
# imag for BDK runtime
RUN microdnf update -y \
    && microdnf install -y findutils \
    && microdnf clean all

# Install poetry
RUN python3 -m venv /poetry \
    && /poetry/bin/pip install -U pip setuptools keyrings.codeartifact \
    && /poetry/bin/pip install poetry \
    && /poetry/bin/poetry config virtualenvs.create false

# Set working directory
WORKDIR /book

# Copy the Python requirements file and install Python dependencies
COPY pyproject.toml poetry.lock /book/

# Install dependencies
RUN --mount=type=secret,id=aws,target=/root/.aws/credentials /poetry/bin/poetry install --only main --no-root \
    && rm -Rf /root/.cache \
    && rm -Rf /root/.config \
    && find /opt/python/versions -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete \
    && find /opt/python/versions -type d -name "test" -exec rm -rf {} + \
    && find /opt/python/versions -type d -name "__pycache__" -exec rm -rf {} +

# Copy project
ADD . ./

# Install the current project
RUN --mount=type=secret,id=aws,target=/root/.aws/credentials /poetry/bin/poetry build -f wheel -n \
    && pip install --no-deps dist/*.whl

# Final image
FROM ${BDK_RUNTIME_IMAGE_URI}

# Copy python environemnt
COPY --from=builder /opt/python/versions /opt/python/versions
RUN chmod -R 777 /opt/python