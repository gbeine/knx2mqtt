FROM python:3-alpine

ENV LOGDIR="/var/log/knx2mqtt"

COPY . /app

WORKDIR /app
RUN apk add --no-cache gcc musl-dev linux-headers
RUN pip install -r requirements.txt
RUN pip install -e knx2mqtt
RUN apk del gcc musl-dev linux-headers

# Logging
RUN mkdir -p $LOGDIR

# Remove default config file -> require mount
RUN rm knx2mqtt.yaml

EXPOSE 12399/udp
CMD ["/bin/sh", "-c", "touch $LOGDIR/.tmpfs && python3 bin/knx2mqtt"]
