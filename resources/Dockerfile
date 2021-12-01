FROM python:3.8

ARG CONNECT_CLI_VERSION

RUN pip install -U pip && pip install poetry && mkdir -p /root/.config/pypoetry \
    && echo "[virtualenvs]" > /root/.config/pypoetry/config.toml \ 
    && echo "create = false" >> /root/.config/pypoetry/config.toml

COPY ./connect /install_temp/connect
COPY ./pyproject.toml /install_temp/.
COPY ./poetry.lock /install_temp/.
COPY ./README.md /install_temp/.

WORKDIR /install_temp
RUN poetry version ${CONNECT_CLI_VERSION}
RUN poetry build
RUN pip install dist/*.whl

RUN rm -rf /install_temp

RUN groupadd connect && useradd -g connect -d /home/connect -s /bin/bash connect

USER connect

WORKDIR /home/connect
