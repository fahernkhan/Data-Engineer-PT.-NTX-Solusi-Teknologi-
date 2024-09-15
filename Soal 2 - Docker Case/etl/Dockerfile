# Use Python 3.11.4 as the base image
FROM python:3.11.4

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the ETL code into the container
COPY etl.py .

# Run the ETL script when the container starts
CMD ["python", "etl.py"]
