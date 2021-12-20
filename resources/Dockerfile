FROM python:3.8

RUN apt-get update && apt-get install -y fonts-liberation

COPY ./dist /install_temp/dist

WORKDIR /install_temp
RUN pip install dist/*.whl

RUN rm -rf /install_temp

RUN groupadd connect && useradd -g connect -d /home/connect -s /bin/bash connect

USER connect

WORKDIR /home/connect
