# ----------------------------
# Frontend Dockerfile
# Streamlit UI for Smart City Emergency Manager
# ----------------------------
FROM python:3.11-slim

WORKDIR /app

# Copy frontend dependencies (install Streamlit + libs)
COPY frontend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all frontend code
COPY frontend ./frontend

# Expose Streamlit default port
EXPOSE 8501

# Start the Streamlit app
CMD ["streamlit", "run", "frontend/streamlit_app_final.py", "--server.port=8501", "--server.address=0.0.0.0"]
