FROM python:3.14-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libffi-dev zlib-dev jpeg-dev

RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN rm /app/requirements.txt

COPY app.py /app

CMD [ "sh" ]