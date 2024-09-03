FROM python:3-alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY knx2mqtt .

CMD [ "python", "./knx2mqtt" ]
