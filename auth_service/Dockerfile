FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables (NO SECRETS)
ENV FLASK_ENV=production
ENV PORT=5001

EXPOSE 5001

CMD ["python", "main.py"]
