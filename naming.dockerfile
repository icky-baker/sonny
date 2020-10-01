FROM python:3.8.5-buster
ENV WORKDIR=/app/

WORKDIR /app/

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY naming/ /app/
RUN mv /app/naming/env_settings.py.docker /app/naming/env_settings.py
# ENTRYPOINT ["/app/scripts/entrypoint.sh"]

EXPOSE 80
CMD ["python", "manage.py", "runserver"]
