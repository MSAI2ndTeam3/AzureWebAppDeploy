FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Azure OpenAI and Speech API keys will be passed as environment variables
CMD ["python", "app.py"]