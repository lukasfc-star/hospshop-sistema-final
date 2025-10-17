# Use a specific Python version image to avoid unexpected upgrades
# Python 3.11 is still widely supported by pandas and numpy as of 2025
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker layer caching
COPY requirements.txt ./

# Install pinned versions of numpy/pandas before other deps to avoid binary incompatibility issues.
# These versions are compatible with each other and Python 3.11.
RUN pip install --no-cache-dir numpy==2.0.0 pandas==2.2.2

# Install the remaining Python dependencies from your requirements file
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that the app will run on
EXPOSE 8080

# Use gunicorn to serve the application. Adjust the module name (app:app)
# to match your actual Python entrypoint if different.
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--workers", "4"]
