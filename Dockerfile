# syntax=docker/dockerfile:1
FROM python:3.8-alpine
WORKDIR /pb-crawler
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 27017
COPY . .
CMD [ "python", "./pb_crawler.py"]