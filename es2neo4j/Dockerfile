FROM debian:jessie


RUN apt-get update && apt-get install -y --no-install-recommends --no-install-suggests python3 python3-pip python3-yaml && \
    rm -rf /var/lib/apt/lists/* 

RUN pip3 install pyprind elasticsearch py2neo

RUN mkdir -p /usr/src/app

COPY . /usr/src/app
WORKDIR /usr/src/app

COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
CMD ["--help"]
