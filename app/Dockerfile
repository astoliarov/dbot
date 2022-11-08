FROM python:3.10

RUN mkdir /app
WORKDIR /app

RUN pip install poetry
RUN apt update && apt install --yes libsodium-dev

COPY poetry.lock pyproject.toml ./
RUN SODIUM_INSTALL=system poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi


COPY . /app

CMD ["python", "main.py"]
