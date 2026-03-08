FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

# CMD exec gunicorn --bind 127.0.0.1:$PORT --workers 1 app:app
CMD ["gunicorn", "--log-level", "info", "--bind", "0.0.0.0:8080", "app:app"]
# CMD ["python", "app.py"]