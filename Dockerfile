FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# RUN alembic upgrade head

# CMD ["uvicorn", "main:main_app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]


