FROM python:3.7-slim

ENV CONTAINER_HOME=/var/www

ADD ./app $CONTAINER_HOME/app
ADD ./requirements.txt $CONTAINER_HOME
WORKDIR $CONTAINER_HOME

RUN pip install -r $CONTAINER_HOME/requirements.txt