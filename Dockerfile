FROM python:3.7

WORKDIR /usr/src/app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -ms /bin/bash exporter
RUN chown exporter:exporter -R .
USER exporter

COPY --chown=exporter . .

CMD ["python", "main.py"]

EXPOSE 9200
