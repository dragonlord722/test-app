FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual code
# If your local folder is backend/app/, this copies 'app/' into '/app/app/'
COPY . .

# Start uvicorn
# We use 'app.main:app' because 'app' is the folder and 'main' is the file
# Correct CMD for Cloud Run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]