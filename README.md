# Car Sharing Analytics Dashboard

An interactive Streamlit dashboard to explore car sharing operational data.

## Features
- KPI metrics: total trips, revenue, distance, average rating
- Interactive charts: revenue over time, trips by city, revenue by brand, rating distribution
- Filters: by city, car brand, and date range
- Pickup location map
- Data chatbot page

## Dataset
Five CSV files: `trips`, `cars`, `customers`, `ratings`, `cities`

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Push this repository to GitHub, then connect it on [share.streamlit.io](https://share.streamlit.io).
