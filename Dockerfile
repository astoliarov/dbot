FROM python:3.11

RUN mkdir /app
WORKDIR /app

COPY Makefile .

RUN make poetry
RUN apt update && apt install --yes libsodium-dev

COPY app /app/app

COPY poetry.lock pyproject.toml ./
RUN SODIUM_INSTALL=system poetry config virtualenvs.create false \
  && make install


CMD ["python", "/app/app/main.py"]
