FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# We'll use pip to install requirements. 
# Since there's no requirements.txt in the repo, we'll install common ones or create it.
RUN pip install --no-cache-dir \
    psycopg2-binary \
    pymongo \
    alive-progress \
    colorama \
    tqdm \
    faker

COPY . .

# Environment variables will be passed via docker-compose
CMD ["python", "generate_all.py"]
