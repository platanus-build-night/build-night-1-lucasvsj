FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Default command (FastAPI server)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]