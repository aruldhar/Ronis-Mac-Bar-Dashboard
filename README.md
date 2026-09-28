# Roni's Mac Bar Sales Dashboard (TAMU Datathon 2024)

An interactive Streamlit dashboard built at TAMU Datathon 2024 by Arul Dhar and Aidan Hernandez for Roni's Mac Bar, a mac-and-cheese restaurant. It turns the restaurant's point-of-sale exports into answers a manager can act on: which ingredients sell, which barely move, and when the rush hits.

![Dashboard overview](assets/dashboard_overview.png)

## What it shows

- **Orders and peak hour** for any single month or all months combined
- **Most popular choice in each category**: cheese, meat, toppings and drizzles
- **Orders by hour of day**, to plan staffing and prep around the lunch and dinner peaks
- **Ingredient popularity charts** by category, toggled from the sidebar

In the June-July 2024 data included here (about 3,700 orders), orders peak at **noon** with a second peak around **6 PM**.

| | |
| --- | --- |
| ![May overview](assets/may_overview_example.png) | ![Cheese popularity](assets/cheese_popularity_example.png) |

Screenshots are from the original hackathon version, which ran on seven months of data (April-October 2024) and counted item rows rather than unique orders.

## How it works

Each row in the export is one item selection, and a single order spans several rows (base, cheese, meat, toppings, drizzle). The app:

1. reads each monthly CSV with the standard `csv` module;
2. counts every ingredient selection into its category;
3. counts each order once by its order ID, and records the hour it was placed;
4. aggregates across months when "All Months" is selected;
5. renders the metrics and bar charts with Streamlit.

## Running it

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

The app finds `data/` relative to its own location, so it can be started from any directory. A dev container is included for GitHub Codespaces.

## Data

Monthly exports go in `data/`, named as in the `month_to_file` mapping in `app/app.py` (for example `june_2024.csv`). Columns used:

| Column | Used for |
| --- | --- |
| `Sent Date` (2nd) | Order hour |
| `Modifier` (3rd) | Ingredient selected |
| `Order ID` (6th) | Counting each order once |

This repository includes June and July 2024. To add another month, drop its export into `data/` and add a line to `month_to_file`.

## Tech stack

Python, Streamlit, pandas, NumPy

## Next steps

- Deploy on Streamlit Community Cloud and link it here
- Add month-over-month trend lines for each ingredient
- Validate columns on load and show a clear message for a malformed file
