FROM python:3.12-slim
EXPOSE 8000
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip3 install --no-cache-dir -r /code/requirements.txt
COPY ./app /code/app
CMD ["gunicorn", "app.main:app", "--timeout", "10", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]