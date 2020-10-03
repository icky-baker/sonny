FROM python:3.8.5-buster
ENV WORKDIR=/app/

WORKDIR /app/

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY Makefile /app/
COPY storage/ /app/

# CMD ["gunicorn", "-b", "0.0.0.0:8000", "naming.wsgi"]
# CMD ["make", "naming_prod"]
CMD ["make", "storage_prod"]
