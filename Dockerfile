FROM python:3.13-alpine

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN rm /app/requirements.txt

COPY app.py /app

CMD [ "sh" ]