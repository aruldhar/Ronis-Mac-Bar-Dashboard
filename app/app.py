import csv
import os
import numpy as np
import streamlit as st
import pandas as pd

# Data folder, resolved relative to this file so the app runs from any directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')

# Mapping from month names to file names
month_to_file = {
    'June': 'june_2024.csv',
    'July': 'july_2024.csv',
}

# Add "All Months" to the dropdown options
month_names = ['All Months'] + list(month_to_file.keys())

# Initialize dictionaries for each ingredient category
ingredient_counts = {
    'cheese': {'Alfredo': 0, 'Cheddar': 0, 'Pepper Jack': 0},
    'meat': {'No Meat': 0, 'Grilled Chicken': 0, 'Pulled Pork': 0, 'Brisket': 0, 'Bacon': 0, 'Ham': 0},
    'toppings': {
        'No Toppings': 0, 'Broccoli': 0, 'Corn': 0, 'Onions': 0, 
        'Jalapenos': 0, 'Tomatoes': 0, 'Bell Peppers': 0, 'Mushrooms': 0, 
        'Pineapple': 0, 'Parmesan': 0, 'Breadcrumbs': 0
    },
    'sauces': {'No Drizzle': 0, 'BBQ': 0, 'Garlic Parmesan': 0, 'Buffalo': 0, 'Pesto': 0, 'Ranch': 0, 'Hot Honey': 0}
}

# Sidebar for selecting month and ingredient filters
st.sidebar.header("Filter Options")
selected_month_name = st.sidebar.selectbox("Select Month", month_names)

# Sidebar options for ingredient categories
selected_cheese = st.sidebar.button("Show Cheese Popularities")
selected_meat = st.sidebar.button("Show Meat Popularities")
selected_topping = st.sidebar.button("Show Topping Popularities")
selected_sauce = st.sidebar.button("Show Drizzle Popularities")
selected_all = st.sidebar.button("Show All Ingredient Popularities")

# Function to load data from a single CSV file and count ingredients
def load_data(file_name):
    ingredient_data = {category: counts.copy() for category, counts in ingredient_counts.items()}
    hours = []
    seen_orders = set()  # Each CSV row is one item selection; an order spans several rows

    with open(os.path.join(DATA_DIR, file_name), 'r', encoding='utf-8', errors='ignore') as file:
        reader = csv.reader(file)
        header = next(reader, None)

        for row in reader:
            try:
                order_time = row[1].split()[1].split(":")[0]
                order_id = row[5]
                if order_id not in seen_orders:  # count each order (and its hour) once
                    seen_orders.add(order_id)
                    hours.append(order_time)
    
                # Count ingredients
                ingredient = row[2]
                for category in ingredient_data:
                    if ingredient in ingredient_data[category]:
                        ingredient_data[category][ingredient] += 1

            except Exception:
                continue

    return ingredient_data, hours, len(seen_orders)

# Function to load data for all months and aggregate
def load_all_months_data():
    combined_ingredient_data = {category: counts.copy() for category, counts in ingredient_counts.items()}
    combined_hours = []
    total_orders = 0  # Initialize total orders for all months

    for file_name in month_to_file.values():
        monthly_data, monthly_hours, monthly_orders = load_data(file_name)
        
        # Aggregate ingredient counts
        for category in combined_ingredient_data:
            for ingredient in combined_ingredient_data[category]:
                combined_ingredient_data[category][ingredient] += monthly_data[category][ingredient]

        # Combine hours data
        combined_hours.extend(monthly_hours)
        total_orders += monthly_orders  # Add monthly orders to total

    return combined_ingredient_data, combined_hours, total_orders

# Load data based on the selected month
if selected_month_name == 'All Months':
    ingredient_data, hours, total_orders = load_all_months_data()
else:
    ingredient_data, hours, total_orders = load_data(month_to_file[selected_month_name])

# Dashboard Title
st.title("Roni's Mac Bar Dashboard")
st.subheader(f"Overview for {'All Months' if selected_month_name == 'All Months' else selected_month_name + ' 2024'}")

# Display total sales for the selected month
st.write(f"**Total Sales for {selected_month_name}:** {total_orders} orders")

# Function to convert 24-hour format to 12-hour format with AM/PM
def convert_to_12_hour_format(hour):
    hour = int(hour)  # Convert to integer to handle the hours correctly
    if hour == 0:
        return "12:00 AM"
    elif hour == 12:
        return "12:00 PM"
    elif hour < 12:
        return f"{hour}:00 AM"
    else:
        return f"{hour - 12}:00 PM"

# Get the most popular hour and convert to 12-hour format with AM/PM
most_popular_hour = pd.Series(hours).value_counts().idxmax()
most_popular_time = convert_to_12_hour_format(most_popular_hour)  # Convert hour to 12-hour format
st.write(f"Most Popular Hour: {most_popular_time}")

# Data Insights section (moved here after most popular hour)
st.subheader("Data Insights")

# Function to get the most popular item for each ingredient category
def get_most_popular_items(data):
    most_popular = {}
    for category, items in data.items():
        most_popular[category] = max(items, key=items.get)
    return most_popular

# Get the most popular items for each ingredient category
most_popular_items = get_most_popular_items(ingredient_data)

# Display the most popular items in each category
st.write("Most popular ingredients for each category:")
for category, item in most_popular_items.items():
    st.write(f"- {category.capitalize()}: {item} with {ingredient_data[category][item]} orders")

# Monthly Orders by Hour
st.subheader("Orders by Hour")
hour_counts = pd.Series(hours).value_counts().sort_index()
st.bar_chart(hour_counts)

# Function to plot ingredient popularity
def plot_ingredient_popularity(data, category):
    labels = list(data[category].keys())
    counts = list(data[category].values())
    df = pd.DataFrame({category: labels, 'Count': counts})

    # Ensure all ingredients are represented, even with zero counts
    all_labels = list(ingredient_counts[category].keys())
    for label in all_labels:
        if label not in df[category].values:
            df = pd.concat([df, pd.DataFrame({category: [label], 'Count': [0]})], ignore_index=True)

    # Re-sort the DataFrame to maintain the correct order
    df = df.set_index(category).reindex(all_labels).reset_index()
    st.bar_chart(df.set_index(category))

# Display graphs based on user selection
if selected_cheese:
    st.subheader("Cheese Popularity")
    plot_ingredient_popularity(ingredient_data, 'cheese')
if selected_meat:
    st.subheader("Meat Popularity")
    plot_ingredient_popularity(ingredient_data, 'meat')
if selected_topping:
    st.subheader("Topping Popularity")
    plot_ingredient_popularity(ingredient_data, 'toppings')
if selected_sauce:
    st.subheader("Sauce Popularity")
    plot_ingredient_popularity(ingredient_data, 'sauces')
if selected_all:
    st.subheader("Cheese Popularity")
    plot_ingredient_popularity(ingredient_data, 'cheese')
    st.subheader("Meat Popularity")
    plot_ingredient_popularity(ingredient_data, 'meat')
    st.subheader("Topping Popularity")
    plot_ingredient_popularity(ingredient_data, 'toppings')
    st.subheader("Sauce Popularity")
    plot_ingredient_popularity(ingredient_data, 'sauces')
