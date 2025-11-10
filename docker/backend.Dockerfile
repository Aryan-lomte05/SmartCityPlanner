# ----------------------------
# Backend Dockerfile
# Smart City Emergency Manager
# ----------------------------
FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files
COPY backend ./backend

# Expose backend port
EXPOSE 8000

# Command to start FastAPI server
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
