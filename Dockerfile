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

# Run Streamlit app using the Azure-provided PORT
CMD ["sh", "-c", "streamlit run streamlitApp.py --server.address=0.0.0.0 --server.port=${PORT} --server.enableCORS=false --server.enableXsrfProtection=false"]