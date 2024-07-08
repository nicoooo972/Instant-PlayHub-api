FROM ubuntu:latest
LABEL authors="nicolas"

FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]