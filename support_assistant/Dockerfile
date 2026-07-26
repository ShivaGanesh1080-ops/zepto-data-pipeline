FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app/ ./app/
COPY docs/ ./docs/

# Explicitly create chroma_db directory to ensure it is available for SQLite
RUN mkdir -p /app/chroma_db

# Expose port
EXPOSE 7860

# Command to run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
