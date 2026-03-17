FROM python:3.9-slim

WORKDIR /app

RUN pip install prometheus-client

COPY stream_monitor.py .

EXPOSE 8000

CMD ["python", "stream_monitor.py"]