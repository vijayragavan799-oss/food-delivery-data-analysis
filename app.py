# ==============================
# IMPORTS
# ==============================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
from datetime import datetime
import numpy as np
import io

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Food Delivery Analytics",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# CUSTOM STYLING
# ==============================
st.markdown("""
<style>
    /* Clean, professional styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        border-bottom: 2px solid #e6e6e6;
    }
    
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #4CAF50;
        height: 100%;
    }
    
    .chart-container {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    
    .section-title {
        color: #2c3e50;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .filter-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #45a049;
        transform: translateY(-1px);
        transition: all 0.3s ease;
    }
    
    /* Data table styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Status indicators */
    .status-delivered { color: #4CAF50; }
    .status-cancelled { color: #f44336; }
    .status-pending { color: #ff9800; }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .metric-card {
            margin-bottom: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==============================
# HEADER
# ==============================
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; color: #2c3e50;">🍽️ Food Delivery Dashboard</h1>
    <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 1.1rem;">
        Track performance, analyze trends, and make data-driven decisions
    </p>
</div>
""", unsafe_allow_html=True)

# ==============================
# DATABASE CONNECTION
# ==============================
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "sql", "food_delivery.db")

@st.cache_data(ttl=300)
def load_data():
    """Load data from SQLite database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM food_orders", conn)
        conn.close()
        
        # Standardize column names for consistency
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'value' in col_lower or 'amount' in col_lower or 'total' in col_lower:
                column_mapping[col] = 'order_value'
            elif 'time' in col_lower and 'delivery' in col_lower:
                column_mapping[col] = 'delivery_time'
            elif 'status' in col_lower:
                column_mapping[col] = 'order_status'
            elif 'cuisine' in col_lower:
                column_mapping[col] = 'cuisine_type'
            elif 'date' in col_lower or 'time' in col_lower:
                column_mapping[col] = 'order_date'
        
        df = df.rename(columns=column_mapping)
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        # Create sample data for demonstration
        np.random.seed(42)
        n = 5000
        data = {
            'order_id': [f'ORD{str(i).zfill(5)}' for i in range(1, n+1)],
            'order_value': np.random.uniform(10, 100, n).round(2),
            'delivery_time': np.random.uniform(15, 60, n).round(1),
            'order_status': np.random.choice(['Delivered', 'Cancelled', 'In Progress', 'Ready for Pickup'], n, p=[0.75, 0.08, 0.12, 0.05]),
            'cuisine_type': np.random.choice(['Italian', 'Chinese', 'Mexican', 'Indian', 'Japanese', 'American', 'Thai'], n),
            'city': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'], n),
            'order_date': pd.date_range('2024-01-01', periods=n, freq='H'),
            'payment_method': np.random.choice(['Credit Card', 'Debit Card', 'PayPal', 'Cash'], n),
            'customer_rating': np.random.choice([1, 2, 3, 4, 5], n, p=[0.02, 0.05, 0.13, 0.3, 0.5])
        }
        return pd.DataFrame(data)

# Load the data
df = load_data()

if df.empty:
    st.warning("⚠️ No data available in the database.")
    st.stop()

# ==============================
# SIDEBAR - CLEAN FILTERS
# ==============================
with st.sidebar:
    st.markdown("### 🔍 Filters")
    st.markdown("---")
    
    filtered_df = df.copy()
    
    # Date filter
    if 'order_date' in df.columns:
        try:
            df['order_date'] = pd.to_datetime(df['order_date'])
            min_date = df['order_date'].min().date()
            max_date = df['order_date'].max().date()
            
            date_range = st.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                help="Filter orders by date range"
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_df = filtered_df[
                    (filtered_df['order_date'].dt.date >= start_date) & 
                    (filtered_df['order_date'].dt.date <= end_date)
                ]
        except:
            pass
    
    # City filter
    if 'city' in df.columns:
        cities = ['All'] + sorted(df['city'].dropna().unique().tolist())
        selected_city = st.selectbox("City", cities, help="Filter by city")
        if selected_city != 'All':
            filtered_df = filtered_df[filtered_df['city'] == selected_city]
    
    # Cuisine filter
    if 'cuisine_type' in df.columns:
        cuisines = ['All'] + sorted(df['cuisine_type'].dropna().unique().tolist())
        selected_cuisine = st.selectbox("Cuisine Type", cuisines, help="Filter by cuisine type")
        if selected_cuisine != 'All':
            filtered_df = filtered_df[filtered_df['cuisine_type'] == selected_cuisine]
    
    # Status filter
    if 'order_status' in df.columns:
        statuses = ['All'] + sorted(df['order_status'].dropna().unique().tolist())
        selected_status = st.selectbox("Order Status", statuses, help="Filter by order status")
        if selected_status != 'All':
            filtered_df = filtered_df[filtered_df['order_status'] == selected_status]
    
    # Order value range
    if 'order_value' in df.columns:
        min_val = float(df['order_value'].min())
        max_val = float(df['order_value'].max())
        
        value_range = st.slider(
            "Order Value Range ($)",
            min_val,
            max_val,
            (min_val, max_val),
            help=f"Range: ${min_val:.2f} - ${max_val:.2f}"
        )
        filtered_df = filtered_df[
            (filtered_df['order_value'] >= value_range[0]) & 
            (filtered_df['order_value'] <= value_range[1])
        ]
    
    st.markdown("---")
    
    # Download buttons - FIXED EXCEL DOWNLOAD
    st.markdown("### 📥 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="CSV",
            data=csv_data,
            file_name=f"food_delivery_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            help="Download filtered data as CSV",
            use_container_width=True
        )
    
    with col2:
        # FIX: Create Excel file in memory
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Food Delivery Data')
        
        excel_data = excel_buffer.getvalue()
        
        st.download_button(
            label="Excel",
            data=excel_data,
            file_name=f"food_delivery_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download filtered data as Excel",
            use_container_width=True
        )
    
    # Summary stats
    st.markdown("---")
    st.markdown("### 📊 Summary")
    st.markdown(f"**Total Records:** {len(filtered_df):,}")
    if len(filtered_df) > 0:
        if 'order_value' in filtered_df.columns:
            st.markdown(f"**Total Revenue:** ${filtered_df['order_value'].sum():,.2f}")
        if 'order_status' in filtered_df.columns:
            delivered_pct = (filtered_df['order_status'] == 'Delivered').mean() * 100
            st.markdown(f"**Delivery Rate:** {delivered_pct:.1f}%")

# ==============================
# KEY METRICS
# ==============================
st.markdown("### 📈 Key Performance Indicators")

# Calculate metrics with safe checks
total_orders = len(filtered_df)

# Check if columns exist and calculate metrics
total_revenue = filtered_df.get('order_value', pd.Series([0])).sum()
avg_order_value = filtered_df.get('order_value', pd.Series([0])).mean()
avg_delivery_time = filtered_df.get('delivery_time', pd.Series([0])).mean()

# Calculate cancellation rate
if 'order_status' in filtered_df.columns:
    cancelled_orders = filtered_df['order_status'].str.contains('cancel', case=False).sum()
    cancellation_rate = (cancelled_orders / total_orders * 100) if total_orders > 0 else 0
else:
    cancellation_rate = 0

# Calculate average rating
avg_rating = filtered_df.get('customer_rating', pd.Series([0])).mean()

# Display metrics in cards
metric_cols = st.columns(5)

with metric_cols[0]:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #3498db;">
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">Total Orders</div>
        <div style="font-size: 2rem; font-weight: 600; color: #2c3e50;">{total_orders:,}</div>
        <div style="font-size: 0.8rem; color: #666; margin-top: 0.5rem;">
            {len(df):,} total in database
        </div>
    </div>
    """, unsafe_allow_html=True)

with metric_cols[1]:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #2ecc71;">
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">Total Revenue</div>
        <div style="font-size: 2rem; font-weight: 600; color: #2c3e50;">${total_revenue:,.0f}</div>
        <div style="font-size: 0.8rem; color: #666; margin-top: 0.5rem;">
            ${filtered_df.get('order_value', pd.Series([0])).median():.0f} median
        </div>
    </div>
    """, unsafe_allow_html=True)

with metric_cols[2]:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #9b59b6;">
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">Avg Order Value</div>
        <div style="font-size: 2rem; font-weight: 600; color: #2c3e50;">${avg_order_value:.2f}</div>
        <div style="font-size: 0.8rem; color: #666; margin-top: 0.5rem;">
            ${filtered_df.get('order_value', pd.Series([0])).std():.1f} std dev
        </div>
    </div>
    """, unsafe_allow_html=True)

with metric_cols[3]:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #e74c3c;">
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">Cancellation Rate</div>
        <div style="font-size: 2rem; font-weight: 600; color: #2c3e50;">{cancellation_rate:.1f}%</div>
        <div style="font-size: 0.8rem; color: #666; margin-top: 0.5rem;">
            {cancelled_orders:,} cancelled orders
        </div>
    </div>
    """, unsafe_allow_html=True)

with metric_cols[4]:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #f39c12;">
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">Avg Delivery Time</div>
        <div style="font-size: 2rem; font-weight: 600; color: #2c3e50;">{avg_delivery_time:.1f} min</div>
        <div style="font-size: 0.8rem; color: #666; margin-top: 0.5rem;">
            {filtered_df.get('delivery_time', pd.Series([0])).median():.1f} median
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==============================
# VISUALIZATIONS
# ==============================
col1, col2 = st.columns(2)

with col1:
    # Order Status Distribution
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 📦 Order Status Distribution")
    
    if 'order_status' in filtered_df.columns and len(filtered_df) > 0:
        status_counts = filtered_df['order_status'].value_counts()
        
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            color=status_counts.index,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(
            showlegend=True,
            height=350,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='%{label}: %{value} orders (%{percent})'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No status data available")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Delivery Time Distribution
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### ⏱️ Delivery Time Analysis")
    
    if 'delivery_time' in filtered_df.columns and len(filtered_df) > 0:
        fig = px.histogram(
            filtered_df,
            x='delivery_time',
            nbins=30,
            title="",
            labels={'delivery_time': 'Delivery Time (minutes)'},
            color_discrete_sequence=['#3498db']
        )
        
        # Add average line
        avg_delivery = filtered_df['delivery_time'].mean()
        fig.add_vline(
            x=avg_delivery,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Average: {avg_delivery:.1f} min",
            annotation_position="top right"
        )
        
        fig.update_layout(
            height=300,
            showlegend=False,
            bargap=0.1
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No delivery time data available")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Cuisine Popularity
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 🍽️ Cuisine Popularity")
    
    if 'cuisine_type' in filtered_df.columns and len(filtered_df) > 0:
        cuisine_counts = filtered_df['cuisine_type'].value_counts().head(10)
        
        fig = px.bar(
            x=cuisine_counts.values,
            y=cuisine_counts.index,
            orientation='h',
            title="",
            labels={'x': 'Number of Orders', 'y': 'Cuisine Type'},
            color=cuisine_counts.values,
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            height=350,
            showlegend=False,
            xaxis_title="Number of Orders",
            yaxis_title="",
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No cuisine data available")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Revenue Trend
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 📈 Revenue Trend")
    
    if 'order_date' in filtered_df.columns and 'order_value' in filtered_df.columns and len(filtered_df) > 0:
        try:
            # Ensure date column is datetime
            filtered_df['order_date'] = pd.to_datetime(filtered_df['order_date'])
            # Resample by day
            daily_revenue = filtered_df.set_index('order_date')['order_value'].resample('D').sum()
            
            fig = px.line(
                x=daily_revenue.index,
                y=daily_revenue.values,
                title="",
                labels={'x': 'Date', 'y': 'Revenue ($)'}
            )
            
            fig.update_layout(
                height=300,
                showlegend=False,
                xaxis_title="Date",
                yaxis_title="Revenue ($)",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Could not generate revenue trend chart")
    else:
        st.info("No time series data available")
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# ADDITIONAL INSIGHTS
# ==============================
st.markdown("---")
st.markdown("### 💡 Business Insights")

insight_cols = st.columns(3)

with insight_cols[0]:
    if 'customer_rating' in filtered_df.columns and len(filtered_df) > 0:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("##### ⭐ Customer Ratings")
        
        rating_counts = filtered_df['customer_rating'].value_counts().sort_index()
        
        fig = px.bar(
            x=rating_counts.index.astype(str),
            y=rating_counts.values,
            title=f"Average: {filtered_df['customer_rating'].mean():.1f}/5",
            labels={'x': 'Rating', 'y': 'Count'},
            color=rating_counts.values,
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(height=250, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="chart-container" style="height: 250px; display: flex; align-items: center; justify-content: center;">', unsafe_allow_html=True)
        st.markdown("<div style='color: #666;'>No rating data</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with insight_cols[1]:
    if 'payment_method' in filtered_df.columns and len(filtered_df) > 0:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("##### 💳 Payment Methods")
        
        payment_counts = filtered_df['payment_method'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=payment_counts.index,
            values=payment_counts.values,
            hole=.4,
            marker_colors=px.colors.qualitative.Pastel
        )])
        fig.update_layout(height=250, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="chart-container" style="height: 250px; display: flex; align-items: center; justify-content: center;">', unsafe_allow_html=True)
        st.markdown("<div style='color: #666;'>No payment data</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with insight_cols[2]:
    if 'city' in filtered_df.columns and len(filtered_df) > 0:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("##### 🏙️ City Performance")
        
        city_stats = filtered_df.groupby('city').agg({
            'order_value': 'sum',
            'order_id': 'count'
        }).rename(columns={'order_id': 'order_count'}).nlargest(5, 'order_value')
        
        fig = go.Figure(data=[
            go.Bar(
                name='Revenue',
                x=city_stats.index,
                y=city_stats['order_value'],
                yaxis='y',
                offsetgroup=0,
                marker_color='#3498db'
            ),
            go.Bar(
                name='Orders',
                x=city_stats.index,
                y=city_stats['order_count'],
                yaxis='y2',
                offsetgroup=1,
                marker_color='#2ecc71'
            )
        ])
        
        fig.update_layout(
            height=250,
            barmode='group',
            yaxis=dict(title='Revenue ($)', side='left'),
            yaxis2=dict(title='Order Count', side='right', overlaying='y'),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="chart-container" style="height: 250px; display: flex; align-items: center; justify-content: center;">', unsafe_allow_html=True)
        st.markdown("<div style='color: #666;'>No city data</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# DATA TABLE
# ==============================
st.markdown("---")
st.markdown("### 📋 Order Details")

if len(filtered_df) > 0:
    # Show data preview with sorting options
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"Showing **{len(filtered_df):,}** records")
    
    with col2:
        sort_options = []
        if 'order_date' in filtered_df.columns:
            sort_options.append('Most Recent')
        if 'order_value' in filtered_df.columns:
            sort_options.append('Highest Value')
            sort_options.append('Lowest Value')
        if 'delivery_time' in filtered_df.columns:
            sort_options.append('Delivery Time')
        
        sort_by = st.selectbox(
            "Sort by",
            sort_options if sort_options else ['Default'],
            help="Sort the data table"
        )
    
    # Apply sorting
    display_df = filtered_df.copy()
    if sort_by == 'Most Recent' and 'order_date' in filtered_df.columns:
        display_df = display_df.sort_values('order_date', ascending=False)
    elif sort_by == 'Highest Value' and 'order_value' in filtered_df.columns:
        display_df = display_df.sort_values('order_value', ascending=False)
    elif sort_by == 'Lowest Value' and 'order_value' in filtered_df.columns:
        display_df = display_df.sort_values('order_value', ascending=True)
    elif sort_by == 'Delivery Time' and 'delivery_time' in filtered_df.columns:
        display_df = display_df.sort_values('delivery_time', ascending=True)
    
    # Display data with pagination
    page_size = st.selectbox("Rows per page", [10, 25, 50, 100], index=1)
    
    total_pages = max(1, len(display_df) // page_size + (1 if len(display_df) % page_size else 0))
    page_number = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
    
    start_idx = (page_number - 1) * page_size
    end_idx = min(start_idx + page_size, len(display_df))
    
    # Display the dataframe
    st.dataframe(
        display_df.iloc[start_idx:end_idx],
        use_container_width=True,
        height=400
    )
    
    st.caption(f"Showing rows {start_idx + 1} to {end_idx} of {len(display_df):,}")
else:
    st.info("No data matches the selected filters. Try adjusting your filter criteria.")

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem 0; font-size: 0.9rem;">
    <p>📊 Food Delivery Analytics Dashboard • Last updated: {}</p>
    <p>💡 Tip: Use the sidebar filters to explore different segments of your data</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)