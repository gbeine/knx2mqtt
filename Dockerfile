FROM python:3-alpine

ENV LOGDIR="/var/log/knx2mqtt"
ENV LOGCONFIG_FILE="/config/logging.production.conf"
ENV CONFIG_FILE="/config/knx2mqtt.yaml"
ENV KNX_LOCAL_PORT=12399

COPY . /app

WORKDIR /app
RUN apk add --no-cache gcc musl-dev linux-headers
RUN pip install -r requirements.txt
RUN pip install -e knx2mqtt
RUN apk del gcc musl-dev linux-headers

# Logging
RUN mkdir -p /config
RUN mv logging*.conf /config
RUN mkdir -p $LOGDIR

# Remove default config file -> require mount
RUN rm knx2mqtt.yaml

EXPOSE $KNX_LOCAL_PORT/udp
CMD ["/bin/sh", "-c", "touch $LOGDIR/.tmpfs && python3 bin/knx2mqtt -c $CONFIG_FILE -l $LOGCONFIG_FILE"]
