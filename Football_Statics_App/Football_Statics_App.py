"""Football Statics App - Streamlit UI

This module provides a small Streamlit app to explore a football
player statistics CSV. It is refactored into clear functions so a
developer can maintain and extend it easily.

Usage:
	streamlit run Football_Statics_App.py

The CSV is expected to live next to this file as
`2021_2022_Football_Player_Stats.csv`. Adjust `DEFAULT_DATA_PATH`
or set `DATA_PATH` environment variable if needed.
"""

from pathlib import Path
import logging
from typing import Optional

import pandas as pd
import streamlit as st
import numpy as np

# Constants
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = BASE_DIR / "2021_2022_Football_Player_Stats.csv"
LOGGER = logging.getLogger(__name__)


@st.cache_data
def load_data(path: Optional[Path] = None) -> pd.DataFrame:
	"""Load CSV data into a DataFrame with caching.

	Args:
		path: Path to the CSV file. If None, uses the default path.

	Returns:
		A pandas DataFrame with the loaded data.
	"""
	csv_path = Path(path or DEFAULT_DATA_PATH)
	if not csv_path.exists():
		raise FileNotFoundError(f"Data file not found: {csv_path}")

	# Use ISO-8859-1 to match the original encoding used by the dataset.
	return pd.read_csv(csv_path, encoding="ISO-8859-1")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
	"""Perform minimal, safe cleaning on the dataset.

	- Drop fully empty rows
	- Remove exact duplicate rows
	"""
	result = df.dropna(how="all").drop_duplicates().reset_index(drop=True)
	return result


def show_sample(df: pd.DataFrame, n: int = 10) -> None:
	"""Display a small sample and a simple chart for numeric columns."""
	sample = df.head(n)
	st.subheader("Data sample")
	st.table(sample)

	# Plot numeric columns only to avoid chart errors
	numeric = sample.select_dtypes(include="number")
	if numeric.shape[1] == 0:
		st.info("No numeric columns available for charting.")
	else:
		st.subheader("Line chart of numeric columns (sample)")
		st.line_chart(numeric)


def _first_column(df: pd.DataFrame, candidates):
	"""Return the first column name from candidates that exists in df."""
	for c in candidates:
		if c in df.columns:
			return c
	return None


def compute_kpis(df: pd.DataFrame) -> pd.DataFrame:
	"""Compute analyst KPIs (per-90 and combined defensive metrics).

	Adds columns: Goals_per90, Assists_per90, Shots_per90, G_per_Shot,
	Tackles_Int_per90, PassCompletion (if available).
	"""
	df = df.copy()

	# Helper column names - use first that exists
	goals_col = _first_column(df, ["Goals", "G"])
	assists_col = _first_column(df, ["Assists", "Ast", "A"])
	shots_col = _first_column(df, ["Shots", "Sh"])
	minutes_col = _first_column(df, ["Min", "Mins", "Minutes"])
	tackles_col = _first_column(df, ["Tkl", "Tackles"])
	interceptions_col = _first_column(df, ["Int", "Interceptions"])

	# Ensure minutes is numeric and non-zero where reasonable
	if minutes_col is None:
		df["_Min"] = 0
		minutes_col = "_Min"
	df[minutes_col] = pd.to_numeric(df[minutes_col], errors="coerce").fillna(0)
	minutes = df[minutes_col].replace(0, pd.NA)

	def per90(col):
		if col is None:
			return pd.Series([pd.NA] * len(df), index=df.index)
		return (pd.to_numeric(df[col], errors="coerce") / minutes) * 90

	df["Goals_per90"] = per90(goals_col)
	df["Assists_per90"] = per90(assists_col)
	df["Shots_per90"] = per90(shots_col)

	# Goals per shot (efficiency)
	if goals_col and shots_col:
		g = pd.to_numeric(df[goals_col], errors="coerce")
		s = pd.to_numeric(df[shots_col], errors="coerce")
		df["Goals_per_Shot"] = (g / s).replace([pd.NA, np.inf, -np.inf], pd.NA)
	else:
		df["Goals_per_Shot"] = pd.NA

	# Defensive action per 90 (Tkl + Int)
	if tackles_col or interceptions_col:
		t = pd.to_numeric(df[tackles_col], errors="coerce") if tackles_col else 0
		itc = pd.to_numeric(df[interceptions_col], errors="coerce") if interceptions_col else 0
		df["Tkl_Int_per90"] = ((t.fillna(0) + itc.fillna(0)) / minutes) * 90
	else:
		df["Tkl_Int_per90"] = pd.NA

	# Pass completion - try a few possible names
	pass_comp_col = _first_column(df, ["PasTotCmp%", "PasTotCmp", "PasCmp%", "PasCmp"])
	if pass_comp_col:
		# remove percent sign if present in values
		df["PassCompletion"] = pd.to_numeric(df[pass_comp_col].astype(str).str.replace('%', ''), errors='coerce')
	else:
		df["PassCompletion"] = pd.NA

	return df


def main() -> None:
	"""Main Streamlit app entry point."""
	st.set_page_config(layout="wide", page_title="Football Stats Dashboard")
	st.title("Football Stats Dashboard")
	st.markdown(
		"A lightweight dashboard to explore the 2021-2022 football player statistics dataset."
	)

	# Load data (respect secrets / env override)
	env_path = None
	try:
		if st.secrets and "DATA_PATH" in st.secrets:
			env_path = Path(st.secrets["DATA_PATH"])
	except Exception:
		env_path = None

	try:
		data = load_data(env_path or DEFAULT_DATA_PATH)
	except Exception as exc:
		LOGGER.exception("Failed to load data")
		st.error(f"Failed to load data: {exc}")
		return

	data = clean_data(data)

	# Prepare numeric columns and a safe copy for display
	df = data.copy()
	# Convert columns that look numeric but may be strings to numeric
	for col in df.columns:
		if df[col].dtype == object:
			df[col] = pd.to_numeric(df[col].str.replace('%', '').str.replace(',', ''), errors='coerce')

	# Compute derived KPIs (per-90 metrics, defensive combos, pass completion)
	df = compute_kpis(df)

	# Sidebar filters
	st.sidebar.header("Filters")
	squads = ["All"] + sorted(df["Squad"].dropna().unique().tolist()) if "Squad" in df.columns else ["All"]
	teams = st.sidebar.multiselect("Team (Squad)", squads, default=["All"]) if squads else []
	positions = ["All"] + sorted(df["Pos"].dropna().unique().tolist()) if "Pos" in df.columns else ["All"]
	pos = st.sidebar.multiselect("Position (Pos)", positions, default=["All"]) if positions else []

	min_minutes = int(df["Min"].min()) if "Min" in df.columns else 0
	max_minutes = int(df["Min"].max()) if "Min" in df.columns else 10000
	minutes = st.sidebar.slider("Min minutes played", min_minutes, max_minutes, (min_minutes, max_minutes))

	# Top N selector
	top_n = st.sidebar.slider("Top N players to show", 5, 50, 10)

	# Apply filters
	mask = pd.Series(True, index=df.index)
	if teams and "All" not in teams:
		mask &= df["Squad"].isin(teams)
	if pos and "All" not in pos:
		mask &= df["Pos"].isin(pos)
	if "Min" in df.columns:
		mask &= df["Min"].between(minutes[0], minutes[1])

	filtered = df[mask].copy()

	# KPIs
	st.subheader("Key Metrics")
	k1, k2, k3, k4 = st.columns(4)
	total_players = int(filtered.shape[0])
	avg_goals = float(filtered["Goals"].mean()) if "Goals" in filtered.columns else 0.0
	avg_assists = float(filtered["Assists"].mean()) if "Assists" in filtered.columns else 0.0
	avg_minutes = float(filtered["Min"].mean()) if "Min" in filtered.columns else 0.0

	k1.metric("Players", f"{total_players}")
	k2.metric("Avg Goals", f"{avg_goals:.2f}")
	k3.metric("Avg Assists", f"{avg_assists:.2f}")
	k4.metric("Avg Minutes", f"{avg_minutes:.0f}")

	# Main layout: left = charts, right = details
	left, right = st.columns((3, 2))

	with left:
		# Additional analyst-focused KPIs and views
		st.subheader("Top Players (per 90)")
		if "Goals_per90" in df.columns:
			top_by_goals90 = filtered.sort_values("Goals_per90", ascending=False).head(top_n)[["Player", "Squad", "Pos", "Goals_per90", "Goals", "Min"]]
			st.write("Top players by Goals per 90 (min filter applied)")
			st.dataframe(top_by_goals90.reset_index(drop=True))
			try:
				import altair as alt

				st.altair_chart(
					alt.Chart(top_by_goals90.reset_index()).mark_bar().encode(
						x=alt.X("Goals_per90", title="Goals per 90"),
						y=alt.Y("Player", sort="-x", title=None),
						tooltip=["Player", "Goals_per90", "Goals", "Min"],
					),
					use_container_width=True,
				)
			except Exception:
				st.bar_chart(top_by_goals90.set_index("Player")["Goals_per90"])

		st.subheader("Position-level KPIs (per 90)")
		if "Pos" in filtered.columns and "Goals_per90" in filtered.columns:
			pos_kpis = (
				filtered.groupby("Pos")[ ["Goals_per90", "Assists_per90", "Shots_per90", "Tkl_Int_per90"] ]
				.mean()
				.fillna(0)
			)
			st.dataframe(pos_kpis)
			try:
				import altair as alt

				pos_chart = pos_kpis.reset_index().melt(id_vars=["Pos"], var_name="Metric", value_name="Value")
				chart = alt.Chart(pos_chart).mark_bar().encode(
					x=alt.X("Value", title="Value (mean per90)"),
					y=alt.Y("Pos", sort="-x"),
					color="Metric",
					tooltip=["Pos", "Metric", "Value"],
				)
				st.altair_chart(chart, use_container_width=True)
			except Exception:
				st.bar_chart(pos_kpis)

		st.subheader("Distribution of Goals per 90")
		if "Goals_per90" in filtered.columns:
			try:
				import altair as alt

				hist = alt.Chart(filtered.dropna(subset=["Goals_per90"]).reset_index()).mark_bar().encode(
					alt.X("Goals_per90", bin=alt.Bin(maxbins=30)),
					y="count()",
				)
				st.altair_chart(hist, use_container_width=True)
			except Exception:
				st.write(filtered["Goals_per90"].dropna().hist())
		st.subheader("Top Scorers")
		if "Goals" in filtered.columns:
			top_scorers = filtered.sort_values("Goals", ascending=False).head(top_n)[["Player", "Squad", "Pos", "Goals", "Shots"]]
			st.dataframe(top_scorers.reset_index(drop=True))
			# Bar chart
			chart_df = top_scorers.set_index("Player")["Goals"]
			st.bar_chart(chart_df)
		else:
			st.info("No 'Goals' column available to show top scorers.")

		st.subheader("Goals vs Shots")
		if all(col in filtered.columns for col in ["Goals", "Shots"]):
			scatter = filtered[["Player", "Goals", "Shots"]].dropna()
			if scatter.shape[0] > 0:
				import altair as alt

				chart = alt.Chart(scatter).mark_circle(size=60).encode(
					x=alt.X("Shots", scale=alt.Scale(zero=True)),
					y=alt.Y("Goals", scale=alt.Scale(zero=True)),
					tooltip=["Player", "Goals", "Shots"]
				).interactive()
				st.altair_chart(chart, use_container_width=True)
			else:
				st.info("Not enough data for Goals vs Shots chart.")
		else:
			st.info("Missing 'Goals' or 'Shots' for scatter chart.")

		st.subheader("Correlation Heatmap (numeric features)")
		num = filtered.select_dtypes(include="number")
		if num.shape[1] >= 2:
			corr = num.corr()
			import matplotlib.pyplot as plt
			import seaborn as sns

			fig, ax = plt.subplots(figsize=(8, 6))
			sns.heatmap(corr, ax=ax, cmap="vlag", center=0)
			st.pyplot(fig)
		else:
			st.info("Not enough numeric columns to compute correlation.")

	with right:
		st.subheader("Player Details & Filters")
		st.write("Use the table below to inspect players. Clicking a row shows details.")
		st.dataframe(filtered.head(200))

		st.subheader("Download")
		csv = filtered.to_csv(index=False)
		st.download_button("Download filtered data (CSV)", csv, file_name="football_filtered.csv")

	st.markdown("---")
	st.caption("Dashboard built for quick exploratory analysis. Ask me to add custom KPIs or visualizations.")


if __name__ == "__main__":
	main()