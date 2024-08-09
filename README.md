<img src="src/openweather/data/icon.svg" width="128" height="128">

# OpenWeather Book

OpenWeather book enables users to fetch real-time temperature data for any city worldwide via the OpenWeather API. 

## Prerequisites
Before you begin, ensure you have the following installed on your system:

### Python 3.11
The project is developed with Python 3.11. We recommend using Pyenv to manage your Python versions.

To manage Python 3.11 with Pyenv, follow these steps:

#### Install Pyenv
If you haven't installed Pyenv yet, you can find the installation instructions on the Pyenv GitHub page. The 
installation process varies depending on your operating system.

#### Install Python 3.11
Once Pyenv is installed, you can install Python 3.11 using the following command:


```shell
pyenv install 3.11
```
 
### Poetry
Poetry is used for dependency management and packaging in this project. 

#### Install Poetry
Run the following command to install Poetry:

```shell
curl -sSL https://install.python-poetry.org | python3 -
```

## Setting Up the Project

### Clone the Repository
Ensure you have the necessary permissions to access the repository and clone it to your local machine:

```shell
git clone <some repository>
cd bdk
```

### Install Dependencies
Use Poetry to install all required dependencies in an isolated environment. This book is dependent on BDK API, which
requires authentication prior to being able to use it.

```shell
poetry config http-basic.bdk aws $(aws codeartifact get-authorization-token --domain-owner 719468614044 --domain kognitos --query 'authorizationToken' --output text)
```

```shell
poetry install
```

### Activate pre-commit hooks [OPTIONAL]
To enforce conventional commits format:

```shell
pre-commit install --hook-type commit-msg
```

## Building the Project
To build the project, run:

```shell
poetry build
```

## Running Tests
This book uses Pytest as its test runner. You can execute it using the following command:

```shell
poetry run tests
```

## Formatting Code
This book uses black and isort as its source formatter. You can execute it using the following command:

```shell
poetry run format
```

## Linting Code
This book uses pylint as its source linter. You can execute it using the following command:

```shell
poetry run lint
```

## Building Docker image using BDK Runtime
In order to deploy the book, a docker image must be build that wraps the book with the BDK runtime. The BDK runtime base
image is hosted in a private ECR which requires authentication. You can do so as follows:

```shell
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 719468614044.dkr.ecr.us-west-2.amazonaws.com
```

```shell
docker build --build-arg CODE_ARTIFACT_TOKEN="$(aws codeartifact get-authorization-token --domain-owner 719468614044 --domain kognitos --query 'authorizationToken' --output text)" .
```
