FROM python:3.8

ADD requirements.txt ./
RUN pip install -r requirements.txt

RUN apt-get update && apt-get -y install lynx less vim npm
RUN npm install -g readability-cli

