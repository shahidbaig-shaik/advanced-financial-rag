FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Make the start script executable
RUN chmod +x start.sh

# Expose the port Render uses for web services (we will map Streamlit to this port)
EXPOSE 8502

# Run the unified start script
CMD ["./start.sh"]
