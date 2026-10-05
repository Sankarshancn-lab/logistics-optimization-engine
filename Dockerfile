FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./logistics_engine

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "logistics_engine.api.app:api_app", "--host", "0.0.0.0", "--port", "8000"]
