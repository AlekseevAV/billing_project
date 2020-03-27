FROM python:3.7-alpine

# Dockerize
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# python
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/
WORKDIR /app

RUN set -ex \
  && apk add postgresql-libs jpeg-dev zlib-dev freetype-dev libjpeg-turbo-dev libpng-dev libxslt-dev unrar mariadb-connector-c-dev \
  && apk add --no-cache --virtual .build-deps \
            g++ \
            gcc \
            git \
            make \
            libc-dev \
            musl-dev \
            linux-headers \
            pcre-dev \
            postgresql-dev \
            python3-dev \
            build-base \
            # criptography deps
            libffi-dev \
  && pip install -r requirements.txt \
  && apk del .build-deps

COPY . /app

EXPOSE 8000

CMD ["gunicorn", "-w", "3", "--bind", ":8000", "project.wsgi:application"]
