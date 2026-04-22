# 🧹 Data Cleaning Web App

A simple Streamlit app to upload, clean, and download CSV files.

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

The app opens automatically at **http://localhost:8501**

## Features
- Upload any CSV file
- View raw data with missing-value summary
- Clean with options:
  - Remove duplicate rows
  - Fill missing numbers with 0
  - Fill missing text with "Unknown"
  - Strip whitespace from text
  - Lowercase all text columns
  - Drop fully-empty columns
- View cleaned data with a change log
- Download cleaned CSV
