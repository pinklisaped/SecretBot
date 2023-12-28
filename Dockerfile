FROM python:3.11.2-alpine3.17

# Set work directory
WORKDIR /app
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN \
    apk update && \
    apk add --no-cache --virtual .build-deps gcc unixodbc-dev g++ && \
    pip install --user aiogram -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

# Set args
ARG DB_CONNECT=sqlite:///db/no_secrets.db LOCALIZATION_PATH=localization DEFAULT_LOCALE=en
ENV DB_CONNECT="${DB_CONNECT}" LOCALIZATION_PATH="${LOCALIZATION_PATH}" DEFAULT_LOCALE="${DEFAULT_LOCALE}"

# Copy app
COPY . /app

# Volume
VOLUME /app/db

# Run app
ENTRYPOINT ["python", "bot_worker.py"]