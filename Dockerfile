# Dockerfile
FROM python:3.10-alpine
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN apk add g++ jpeg-dev zlib-dev libjpeg make
RUN pip install --upgrade pip --no-cache-dir && pip install -r requirements.txt --no-cache-dir;
COPY . .
CMD ["python", "main.py"]