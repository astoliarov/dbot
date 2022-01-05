FROM python:3.9

RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN apt update && apt install --yes libsodium-dev
RUN SODIUM_INSTALL=system pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python", "main.py"]
