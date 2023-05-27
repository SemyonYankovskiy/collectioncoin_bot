FROM python:3.10-alpine
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk add --no-cache g++ jpeg-dev zlib-dev libjpeg make


# For cairosvg
RUN apk add --no-cache \
    build-base cairo-dev cairo cairo-tools \
    jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev

COPY requirements.txt .

RUN pip install --upgrade pip --no-cache-dir && pip install -r requirements.txt --no-cache-dir;

COPY . .
CMD ["python", "new_map.py"]