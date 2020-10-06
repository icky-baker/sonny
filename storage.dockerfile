FROM python:3.8.5-buster
ENV WORKDIR=/app/

WORKDIR /app/

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY Makefile /app/
COPY storage/ /app/

CMD ["make", "storage_prod"]
