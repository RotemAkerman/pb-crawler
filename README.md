# PB-Crawler

Simple pastebin crawler.

## Description

This program crawls pastebin.com and stores the most recent "pastes" in a structured data model in MongoDB.
Program consists of 2 services:
* mongodb
    * latest mongo image with default settings, exposing port 27017
* crawler
    * Python script that crawls latest pastes every 2 minutes and upsert to mongodb service.

## Getting Started

### Dependencies

* Docker
* Docker-compose
* Port 27017 should be free

### Running

* cd to project directory and run:
```
docker-compose up

```
or
```
docker-compose up -d
```
(to run everything in the background)

## Author

Rotem Akerman

## Acknowledgments

External python libraries:
* lxml
* pymongo
* python-dateutil
* requests
