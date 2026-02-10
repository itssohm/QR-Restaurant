# STEP 1: Use ECR Public Gallery to avoid Docker Hub 429 Rate Limits
# Official URI for Python 3.12-slim on AWS
FROM public.ecr.aws/docker/library/python:3.12-slim

# STEP 2: Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV APP_HOST=0.0.0.0

# STEP 3: Set working directory
WORKDIR /app

# STEP 4: Install system dependencies
# We combine these and clean up the cache to keep the image small
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# STEP 5: Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# STEP 6: Copy application code
COPY . .

# STEP 7: Create necessary directories
RUN mkdir -p /app/static/uploads /app/reports

# STEP 8: Expose the application port
EXPOSE 8080

# STEP 9: Start the app
# Note: Using python app.py is fine for dev, 
# but in production, you'd usually use 'gunicorn'
CMD ["python", "app.py"]