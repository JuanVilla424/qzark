# Dockerfile
FROM python:3.12-slim

# Create and switch to the /app directory inside the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . /app/

# Run Qzark-like app by default (we'll override command in docker-compose)
CMD ["python", "-m", "src.main"]
