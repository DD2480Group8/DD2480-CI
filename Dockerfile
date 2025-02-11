# Use Python 3.13.1 base image
FROM python:3.13.1-slim

ARG GITHUB_TOKEN
ENV GITHUB_TOKEN=$GITHUB_TOKEN

# Set the working directory in the container
WORKDIR /app

# Install Git and any system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file if dependencies exist
# (Uncomment the next line if you have a requirements.txt)
COPY requirements.txt /app/

# Copy the entire project into the container
COPY . /app

ENV PYTHONUNBUFFERED=1

# Install any dependencies (again, uncomment if requirements.txt exists)
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your server listens on (adjust if necessary)
EXPOSE 8008

# Command to run the server
CMD ["python", "src/app/main.py"]