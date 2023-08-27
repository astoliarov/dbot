FROM python:3.11 as base

RUN mkdir /app
WORKDIR /app

COPY Makefile .

RUN make poetry
RUN apt update && apt install --yes libsodium-dev

COPY src /app/src

COPY poetry.lock pyproject.toml ./
RUN SODIUM_INSTALL=system poetry config virtualenvs.create false \
  && make install


CMD ["python", "/app/src/dbot/main.py"]
