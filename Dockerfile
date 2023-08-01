#FROM python:3.10-alpine
#ENV PYTHONUNBUFFERED 1
#
#WORKDIR /app
#
#RUN pip install --upgrade pip
#RUN apk add --no-cache g++ jpeg-dev zlib-dev libjpeg make
## Install required system dependencies
#
#RUN apk add --no-cache python3-dev libffi-dev openssl-dev gcc musl-dev
#COPY requirements.txt .
#
#RUN pip install --upgrade pip --no-cache-dir && pip install -r requirements.txt --no-cache-dir;
#
#COPY . .
#CMD ["python", "run.py"]

FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "run.py" ]