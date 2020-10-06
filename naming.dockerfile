FROM python:3.8.5-buster
ENV WORKDIR=/app/

WORKDIR /app/

COPY requirements.txt /app/
RUN pip install -r requirements.txt

EXPOSE 80

RUN apt-get update && apt-get -y install cron
COPY naming/core/crontab /etc/cron.d/naming-crontab
RUN chmod 0644 /etc/cron.d/naming-crontab &&\
    crontab /etc/cron.d/naming-crontab &&\
    touch /var/log/cron.log

COPY Makefile /app/
COPY naming/ /app/
RUN mv /app/naming/env_settings.py.docker /app/naming/env_settings.py

# CMD ["gunicorn", "-b", "0.0.0.0:8000", "naming.wsgi"]
# CMD ["make", "naming_prod"]
CMD ["make", "naming_preprod"]
