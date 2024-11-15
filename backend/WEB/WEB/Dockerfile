# Use Python 3.9 as the base image
FROM python:3.10

# Set working directory in container
WORKDIR /app

# Install dependencies from requirements.txt
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy all the project files into the container
COPY . /app

# Expose the Django port
EXPOSE 8000

# Set the environment variable for Celery
ENV CELERY_BROKER_URL=amqp://guest:guest@127.0.0.1:5672//

# Run Django server by default
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]