FROM python:3.9-slim

WORKDIR "/application"
ENV PYTHONPATH=/application

COPY requirements.txt requirements.txt
COPY cointracker ./tracker

RUN pip --version && pip install . --no-cache-dir

COPY ./files/liveness_probe.sh liveness_probe.sh
RUN chmod u+x liveness_probe.sh

ENTRYPOINT ["python","./tracker/main.py"]
