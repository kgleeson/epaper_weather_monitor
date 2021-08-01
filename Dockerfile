FROM python:3.8 AS builder

COPY requirements.txt .
RUN apt-get install -y libfreetype6-dev libxft-dev libjpeg62 libopenjp2-7 libtiff5 libxcb1
RUN pip install --user -r requirements.txt

FROM python:3.8-slim

RUN apt-get update ; \
     apt-get install --no-install-recommends -y \
     cron \
     libfreetype6 \
     libxft-dev \
     libjpeg62 \
     libopenjp2-7 \
     libtiff5 \
     libxcb1 ; \
     apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local:$PATH

RUN chmod a+x entrypoint.sh

CMD [ "sh", "entrypoint.sh" ]