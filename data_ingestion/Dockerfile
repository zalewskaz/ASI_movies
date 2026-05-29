FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py .

COPY . .

CMD ["python", "-m", "data_ingestion.scheduler"]