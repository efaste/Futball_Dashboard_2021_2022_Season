# Football Dashboard App

A Python-based football analytics dashboard for exploring the 2021–2022 player statistics dataset. The project follows these steps: ingest raw CSV data, clean and normalize it, compute analyst-friendly KPIs, and expose interactive insights through a Streamlit app.

## What it does
- Loads football player statistics from CSV
- Cleans missing and duplicate records
- Converts raw metrics into meaningful KPIs
- Filters by team, position, and minutes played
- Displays summary metrics, charts, and player-level analysis
- Exports filtered data as CSV

## Tech stack
- Python
- Streamlit
- pandas
- NumPy
- Altair
- Matplotlib
- Seaborn

## Repository structure
```text
.
├── LICENSE
├── requirements.txt
├── .gitignore
├── Football_Statics_App/
│   ├── Football_Statics_App.py
│   └── 2021_2022_Football_Player_Stats.csv
├── README.md
└── Football_Dashboard_App_README_stub.md
```

## Key KPIs
The app computes derived metrics such as:
- Goals per 90
- Assists per 90
- Shots per 90
- Goals per shot
- Tackles + interceptions per 90
- Pass completion

These metrics help compare players fairly across different minutes played.

## Getting started
```bash
git clone https://github.com/efaste/Footbaal_Dashboard_App.git
cd Footbaal_Dashboard_App
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run Football_Statics_App/Football_Statics_App.py
```

## Dashboard features
- Sidebar filters for squad, position, and minutes
- KPI summary cards
- Top players by per-90 performance
- Position-level comparisons
- Goal vs. shot analysis
- Correlation heatmap
- CSV export for filtered results

## License
See the LICENSE file for details.

This project is a lightweight example of turning raw football data into a clean, analyst-friendly data product.
