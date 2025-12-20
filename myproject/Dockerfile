FROM python:3.12

# Set work directory
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install system dependencies required by packages like lxml, numpy, etc.


# Copy and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose Django port
EXPOSE 8000

# Use JSON array format for CMD (fixes JSONArgsRecommended warning)
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
