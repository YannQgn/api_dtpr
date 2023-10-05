#!/bin/bash
cd client
streamlit run app.py --server.port 8501 &
cd ..
cd server
uvicorn app:app --host 0.0.0.0 --port 8502 --reload &
