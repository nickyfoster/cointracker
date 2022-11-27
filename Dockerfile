FROM python:3.9-slim

WORKDIR "/application"
ENV PYTHONPATH=/application


COPY setup.py setup.py
COPY tracker ./tracker

RUN pip --version && pip install . --no-cache-dir

ENTRYPOINT ["python","./tracker/main.py"]
