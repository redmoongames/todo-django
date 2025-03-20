FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app

RUN echo '#!/bin/bash\n\
echo "Checking database directory..."\n\
DB_DIR=$(dirname $(python -c "from django.conf import settings; print(settings.DATABASES[\"default\"][\"NAME\"])"))\n\
mkdir -p $DB_DIR\n\
echo "Ensuring proper permissions..."\n\
touch $(python -c "from django.conf import settings; print(settings.DATABASES[\"default\"][\"NAME\"])")\n\
chmod 666 $(python -c "from django.conf import settings; print(settings.DATABASES[\"default\"][\"NAME\"])")\n\
echo "Checking Redis connectivity..."\n\
python -c "import redis; r = redis.Redis(host=\"redis\", port=6379, db=1); r.ping()"\n\
REDIS_CHECK=$?\n\
if [ $REDIS_CHECK -ne 0 ]; then\n\
    echo "Failed to connect to Redis. Please make sure Redis is running."\n\
    exit 1\n\
fi\n\
echo "Running database migrations..."\n\
python manage.py migrate --noinput\n\
echo "Starting Django server..."\n\
python manage.py runserver 0.0.0.0:8000\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]
