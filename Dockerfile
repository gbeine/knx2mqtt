FROM python:3-alpine

ENV LOGDIR="/var/log/knx2mqtt"
ENV LOGCONFIG_FILE="/config/logging.production.conf"
ENV CONFIG_FILE="/config/knx2mqtt.yaml"
ENV KNX_LOCAL_PORT=12399

COPY . /app

WORKDIR /app
RUN apk add --no-cache gcc musl-dev libffi-dev linux-headers \
    && pip install -r requirements.txt \
    && pip install -e knx2mqtt \
    && apk del --purge gcc musl-dev libffi-dev linux-headers \
    && rm -rf /var/cache/apk/*

# Logging
RUN mkdir -p /config \
    && mv logging*.conf /config \
    && mkdir -p $LOGDIR

# Remove default config file -> require mount
RUN rm knx2mqtt.yaml

EXPOSE $KNX_LOCAL_PORT/udp
CMD ["/bin/sh", "-c", "touch $LOGDIR/.tmpfs && python3 bin/knx2mqtt -c $CONFIG_FILE -l $LOGCONFIG_FILE"]
