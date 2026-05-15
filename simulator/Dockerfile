FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy simulator code
COPY . .

# Expose port (if simulator has a health endpoint)
EXPOSE 8001

# Run the simulator
CMD ["python", "simulator.py"]

# Made with Bob
