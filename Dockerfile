FROM python:3.11-slim

WORKDIR /app

COPY . /app

WORKDIR /app/bench-p02-context

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "run.py", "--adapter", "adapters.myteam_integrated:Engine", "--out", "l3_report.json"]