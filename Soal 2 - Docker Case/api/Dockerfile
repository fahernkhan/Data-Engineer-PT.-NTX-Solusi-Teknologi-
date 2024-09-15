# Use Python 3.11.4 as the base image
FROM python:3.11.4

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API code into the container
COPY api.py .

# Expose the port that FastAPI will run on
EXPOSE 6000

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "6000"]
