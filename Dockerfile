FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Azure OpenAI and Speech API keys will be passed as environment variables
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]