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

#FROM python:3.9-slim-buster
FROM python:3.8.8
ENV PYTHONUNBUFFERED 1

WORKDIR /app
#RUN apt-get update && apt-get install -y git


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

#RUN git clone https://github.com/geopandas/geopandas.git --branch main --single-branch --depth 1 --shallow-submodules 4b72fb417a4e31ad4ffde7df01927faf54ac362bB

COPY . .

CMD [ "python", "run.py" ]