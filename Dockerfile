FROM piptools:latest

ADD requirements.txt ./
RUN pip install -r requirements.txt

# Download spacy's trained pipeline for english
RUN python -m spacy download en_core_web_sm

# Add jupyterlab extensions
RUN pip install jupyterlab_execute_time

# Git is needed for MLFlow tracking
RUN apt-get update -y && apt-get install -y git && apt-get -y install lynx less vim npm
RUN npm install -g readability-cli

ENV PYTHONPATH="/home"