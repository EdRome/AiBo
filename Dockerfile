FROM python:3.11-slim
ARG APP_VERSION
RUN echo "Compilando versión $APP_VERSION"

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
# RUN python -m spacy download es_core_news_sm

COPY . .

# CMD exec gunicorn --bind 127.0.0.1:8080 --workers 1 app:app
CMD ["gunicorn", "--log-level", "info", "--bind", "0.0.0.0:8080", "app:app"]
# CMD ["python", "app.py"]