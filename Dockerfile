# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /
WORKDIR /

# Copy the contents of the app folder into the container
COPY app/ .
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN python3 -m pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Run app.py when the container launches
CMD ["python", "blog.py"]