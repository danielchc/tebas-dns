FROM debian:stable-slim

RUN apt update && apt -y dist-upgrade

RUN apt install -y dnsmasq python3 python3-requests cron procps

COPY entrypoint.sh /entrypoint.sh
COPY update-list.py /update-list.py

RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
