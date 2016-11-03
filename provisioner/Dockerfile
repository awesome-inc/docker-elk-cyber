FROM debian:jessie

RUN apt-get update && apt-get install -y --no-install-suggests --no-install-recommends netcat curl && rm -rf /var/lib/apt/lists/*

COPY provision.sh /
RUN chmod +x /provision.sh

CMD ["/provision.sh"]
