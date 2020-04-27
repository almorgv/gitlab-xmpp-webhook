FROM ubuntu:bionic

ARG APT_PROXY

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV TZ=Europe/Moscow

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# -- Install Pipenv:
RUN set -ex && \
	apt update && \
	apt install python3-pip -y && \
	pip3 install pipenv && \
	rm /etc/apt/apt.conf

# -- Install Application into container:
RUN set -ex && mkdir /app

COPY . /app

WORKDIR /app

RUN set -ex && pipenv --python 3.6 && pipenv sync

EXPOSE 8080/tcp

CMD pipenv run python main.py
