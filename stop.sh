#!/bin/bash

pkill -f "streamlit run app.py --server.port 8501"
pkill -f "uvicorn app:app --host 0.0.0.0 --port 8502 --reload"