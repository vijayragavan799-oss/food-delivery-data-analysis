# ==============================
# IMPORTS
# ==============================
import streamlit as st
import pandas as pd
import sqlite3
import os

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Food Delivery Dashboard", layout="wide")
st.title("🍔 Online Food Delivery Analytics Dashboard")

# ==============================
# DATABASE PATH
# ==============================
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "sql", "food_delivery.db")

if not os.path.exists(DB_PATH):
    st.error("❌ SQLite database not found")
    st.stop()

# ==============================
# LOAD DATA
# ==============================
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM food_orders", conn)
conn.close()

if df.empty:
    st.warning("⚠️ No data found in database")
    st.stop()

# ==============================
# COLUMN AUTO-DETECTION
# ==============================
cols = {c.lower(): c for c in df.columns}

def find_col(candidates):
    for c in candidates:
        if c in cols:
            return cols[c]
    return None

order_value_col = find_col({"order_value", "final_amount", "amount", "total_amount"})
delivery_time_col = find_col({"delivery_time", "delivery_time_min", "delivery_time_minutes"})
status_col = find_col({"order_status", "status"})
cuisine_col = find_col({"cuisine", "cuisine_type"})

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("🔎 Filters")
filtered_df = df.copy()

# City filter
if "city" in cols:
    city_col = cols["city"]
    city_options = sorted(df[city_col].dropna().unique().tolist())
    selected_cities = st.sidebar.multiselect("City", city_options)
    if selected_cities:
        filtered_df = filtered_df[filtered_df[city_col].isin(selected_cities)]

# Cuisine filter
if cuisine_col:
    cuisine_options = sorted(df[cuisine_col].dropna().unique().tolist())
    selected_cuisines = st.sidebar.multiselect("Cuisine", cuisine_options)
    if selected_cuisines:
        filtered_df = filtered_df[filtered_df[cuisine_col].isin(selected_cuisines)]

# Order status filter
if status_col:
    status_options = sorted(df[status_col].dropna().unique().tolist())
    selected_status = st.sidebar.multiselect("Order Status", status_options)
    if selected_status:
        filtered_df = filtered_df[filtered_df[status_col].isin(selected_status)]

# ==============================
# KPIs
# ==============================
total_orders = len(filtered_df)

total_revenue = (
    filtered_df[order_value_col].sum()
    if order_value_col else 0
)

avg_order_value = (
    filtered_df[order_value_col].mean()
    if order_value_col else 0
)

avg_delivery_time = (
    filtered_df[delivery_time_col].mean()
    if delivery_time_col else 0
)

cancel_rate = (
    (filtered_df[status_col].astype(str).str.lower() == "cancelled").sum()
    / total_orders * 100
    if status_col and total_orders > 0 else 0
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📦 Total Orders", total_orders)
c2.metric("💰 Total Revenue", round(total_revenue, 2))
c3.metric("🧾 Avg Order Value", round(avg_order_value, 2))
c4.metric("⏱ Avg Delivery Time", round(avg_delivery_time, 2))
c5.metric("❌ Cancellation Rate (%)", round(cancel_rate, 2))

st.divider()

# ==============================
# KPI SUMMARY (FOR GAMMA)
# ==============================
kpi_summary = pd.DataFrame({
    "Metric": [
        "Total Orders",
        "Total Revenue",
        "Average Order Value",
        "Average Delivery Time",
        "Cancellation Rate (%)"
    ],
    "Value": [
        total_orders,
        round(total_revenue, 2),
        round(avg_order_value, 2),
        round(avg_delivery_time, 2),
        round(cancel_rate, 2)
    ]
})

# ==============================
# DOWNLOAD SECTION (SIDEBAR)
# ==============================
st.sidebar.subheader("⬇️ Download")

st.sidebar.download_button(
    label="📥 Download Filtered Data (CSV)",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_food_delivery_data.csv",
    mime="text/csv"
)

st.sidebar.download_button(
    label="📥 Download KPI Summary (Gamma)",
    data=kpi_summary.to_csv(index=False).encode("utf-8"),
    file_name="gamma_kpi_summary.csv",
    mime="text/csv"
)

# ==============================
# CHARTS
# ==============================
if status_col:
    st.subheader("📊 Order Status Distribution")
    st.bar_chart(filtered_df[status_col].value_counts())

if cuisine_col:
    st.subheader("🍽 Cuisine Popularity")
    st.bar_chart(filtered_df[cuisine_col].value_counts())

st.divider()

# ==============================
# DATA PREVIEW
# ==============================
st.subheader("📄 Filtered Data Preview")
st.dataframe(filtered_df.head(50))
