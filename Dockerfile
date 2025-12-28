FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable buffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential netcat \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY myproject/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt
# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       netcat-openbsd \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app

# Expose Django default port
EXPOSE 8000

# Run migrations then start development server
CMD ["sh", "-c", "python myproject/manage.py migrate --noinput && python myproject/manage.py runserver 0.0.0.0:8000"]
