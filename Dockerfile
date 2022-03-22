# deployment python app with gunicorn and poetry install

FROM python:3.9-slim

COPY . /app
WORKDIR /app

# install poetry
RUN apt-get update && apt-get install -y curl && \ 
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python && \
    . ~/.profile && \
    poetry install && \
    mkdir -p /app/logs

CMD . ~/.profile && poetry run gunicorn app:app -b 0.0.0.0:8000 --config gunicorn.conf.py