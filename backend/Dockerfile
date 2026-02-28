# 1. Minimal base image
FROM python:3.11-slim

# 2. Set working directory
WORKDIR /code

# 3. Copy only the backend requirements first for Docker layer caching
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the app module into the container
COPY app/ ./app/

# 6. Expose the Cloud Run port
EXPOSE 8080

# 7. Start Uvicorn pointing to the new module path (app.main)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]