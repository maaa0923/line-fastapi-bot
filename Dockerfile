FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY credentials.json /app/credentials.json

COPY . .

CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8080"]


