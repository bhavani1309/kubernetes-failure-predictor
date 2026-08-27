# Use official Python base image
FROM python:3.10-slim

# Set environment variables to prevent interactive prompts and allow Streamlit in container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create working directory
WORKDIR /app

# Copy only requirement files first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Now copy the rest of your app
COPY . .

# Expose port for Streamlit
EXPOSE 8501

# Start the Streamlit app with correct host and port
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
