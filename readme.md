Project Title

Online Food Delivery Data Analysis Using Python, SQLite, and Streamlit

Project Objective

To analyze online food delivery data and extract business insights related to customer behavior, order trends, delivery performance, and profitability using Python, SQL, and interactive dashboards.

Dataset Description

The dataset contains approximately 100,000 online food delivery orders with 25+ features covering customer details, order information, restaurant attributes, delivery performance, and financial metrics.

Tools & Technologies

Python

Pandas, NumPy

SQLite

Streamlit

Visual Studio Code

Project Architecture
food_delivery_project/
├── data/raw/
├── src/
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   ├── sqlite_data_loader.py
│   ├── sqlite_analytics_runner.py
│   └── app.py
├── sql/
│   └── food_delivery.db
└── README.md

Data Cleaning & Preprocessing

Handled missing values using mean, median, and mode

Removed or corrected invalid values

Standardized categorical fields

Ensured logical consistency in data

Feature Engineering

Weekday / Weekend classification

Peak hour indicator

Profit margin calculation

Delivery performance categorization

Customer age grouping

Data Storage

The cleaned and engineered dataset was stored in a SQLite database to enable structured querying and efficient analytics.

SQL Analytics

Total orders and revenue analysis

Average order value calculation

Cancellation rate analysis

Delivery performance evaluation

Weekend vs weekday comparison

Dashboard (Streamlit)

An interactive Streamlit dashboard was developed to visualize KPIs, trends, and insights with dynamic filters and real-time data exploration.

Key KPIs

Total Orders

Total Revenue

Average Order Value

Average Delivery Time

Cancellation Rate

Key Business Insights

Peak hours contribute significantly to order volume

Delivery performance impacts cancellation rates

Weekend ordering patterns differ from weekdays

Higher order values tend to yield better profit margins

Conclusion

The project demonstrates an end-to-end data analytics pipeline from raw data processing to SQL-based analytics and interactive dashboard visualization, enabling data-driven decision-making.

How to Run the Project
pip install -r requirements.txt
python src/sqlite_data_loader.py
streamlit run src/app.py

Future Enhancements

Predictive analytics

Cloud deployment

Real-time data integration