#!/bin/bash
# Install packages
pip install --upgrade pip
pip install -r requirements.txt

# Run the Streamlit app
streamlit run streamlitApp.py --server.port=$PORT --server.address=0.0.0.0 --server.enableCORS=false
