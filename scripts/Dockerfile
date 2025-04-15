FROM python:3.9-slim

WORKDIR /scripts

# Install Redis Python client
RUN pip install redis==5.2.1

# Copy the Python script
COPY numbers.py .

# Run the script
CMD ["python", "numbers.py"]