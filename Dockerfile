FROM python:3.10.5-slim-bullseye

# Set the working directory to /app
WORKDIR /app

# Copy requirements.txt to the container at /app
COPY requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy src to the container at /app
COPY src/ /app

# Copy .env to the container at /app
COPY .env /app/.env

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl

# Make port 80 available to the world outside this container
EXPOSE 80

CMD [ "python", "main.py" ]
