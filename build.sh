#!/usr/bin/env bash
# build script for render - installs deps and runs the data pipeline
pip install -r backend/requirements.txt
pip install pandas numpy

# generate and process data
python generate_data.py
python clean_data.py
python analyze.py
