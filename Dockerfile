FROM python:3.10-alpine
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk add --no-cache g++ jpeg-dev zlib-dev libjpeg make

COPY requirements.txt .

RUN pip install --upgrade pip --no-cache-dir && pip install -r requirements.txt --no-cache-dir;

COPY . .
CMD ["python", "new_map.py"]