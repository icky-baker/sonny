FROM python:3.8.5-buster
ENV WORKDIR=/app/

WORKDIR /app/
EXPOSE 80

COPY Makefile /app/

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY naming/ /app/
RUN mv /app/naming/env_settings.py.docker /app/naming/env_settings.py

# CMD ["gunicorn", "-b", "0.0.0.0:8000", "naming.wsgi"]
CMD ["make", "naming_prod"]
