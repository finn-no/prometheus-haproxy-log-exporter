FROM python:3-alpine
COPY . /src
RUN cd /src && python setup.py install && cd / && rm -rf /src
ENTRYPOINT ["/usr/local/bin/prometheus-haproxy-log-exporter"]
