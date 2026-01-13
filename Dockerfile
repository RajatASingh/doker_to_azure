# Base image with Python
FROM python:3.8-slim-buster

# Set working directory inside container
WORKDIR /streamlit-demo

# Copy requirements file
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN python3 -m pip install --upgrade pip \
    && pip3 install -r requirements.txt

# Copy entire project into container
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "streamlitApp.py",  "--server.port=8501", "--server.enableCORS", "false"]