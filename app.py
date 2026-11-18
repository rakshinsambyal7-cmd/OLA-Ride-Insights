import os
import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & OLA THEME STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="OLA Ride Insights | Analytics Dashboard",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #8DC63F;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #A0A0A0;
        margin-bottom: 1.5rem;
    }
    div[data-testid="stMetricValue"] {
        color: #8DC63F;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. LOAD CLEANED DATASET (CACHED FOR SPEED)
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("OLA_Cleaned_July.csv", low_memory=False)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ `OLA_Cleaned_July.csv` not found! Make sure it is in the same folder as `app.py`.")
    st.stop()

# ---------------------------------------------------------
# 3. SIDEBAR NAVIGATION & GLOBAL FILTERS
# ---------------------------------------------------------
st.sidebar.markdown("## 🚖 OLA Ride Insights")
st.sidebar.markdown("End-to-End Business Intelligence & SQL Analytics")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate Sections:",
    ["📊 Executive Overview", "🗄️ 10 SQL Business Queries", "📈 Power BI Dashboard Showcase", "🔍 Interactive Ride Explorer"]
)

st.sidebar.divider()
st.sidebar.markdown("### Global Filters")
vehicle_options = sorted(df["Vehicle_Type"].dropna().astype(str).unique().tolist())
selected_vehicles = st.sidebar.multiselect(
    "Filter by Vehicle Type:",
    options=vehicle_options,
    default=vehicle_options
)

selected_time = st.sidebar.multiselect(
    "Filter by Time of Day:",
    options=["Morning", "Afternoon", "Evening", "Night"],
    default=["Morning", "Afternoon", "Evening", "Night"]
)

filtered_df = df[
    (df["Vehicle_Type"].astype(str).isin(selected_vehicles)) &
    (df["Time_of_Day"].astype(str).isin(selected_time))
]

# ---------------------------------------------------------
# PAGE 1: EXECUTIVE OVERVIEW
# ---------------------------------------------------------
if page == "📊 Executive Overview":
    st.markdown('<div class="main-header">🚖 OLA Ride Insights — July Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Operational performance, revenue drivers, cancellation bottlenecks, and service ratings.</div>', unsafe_allow_html=True)

    total_bookings = len(filtered_df)
    success_df = filtered_df[filtered_df["Booking_Status"] == "Success"]
    success_rate = (len(success_df) / total_bookings * 100) if total_bookings > 0 else 0
    total_revenue = success_df["Booking_Value"].sum()
    avg_driver_rating = filtered_df["Driver_Ratings"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Bookings", f"{total_bookings:,}")
    col2.metric("Success Rate", f"{success_rate:.2f}%")
    col3.metric("Successful Revenue", f"₹ {total_revenue:,.0f}")
    col4.metric("Avg. Driver Rating", f"{avg_driver_rating:.2f} ⭐" if pd.notna(avg_driver_rating) else "N/A")

    st.divider()

    c1, c2 = st.columns([1.4, 1])

    with c1:
        st.subheader("Daily Ride Volume Over Time")
        daily_rides = filtered_df.groupby("Date")["Booking_ID"].count().reset_index(name="Total Rides")
        fig_line = px.line(
            daily_rides, x="Date", y="Total Rides", markers=True,
            color_discrete_sequence=["#8DC63F"]
        )
        fig_line.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_line, use_container_width=True)

    with c2:
        st.subheader("Booking Status Breakdown")
        status_counts = filtered_df["Booking_Status"].value_counts().reset_index()
        status_counts.columns = ["Booking_Status", "Count"]
        fig_pie = px.pie(
            status_counts, names="Booking_Status", values="Count", hole=0.45,
            color_discrete_sequence=["#8DC63F", "#2E3131", "#E74C3C", "#95A5A6"]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ---------------------------------------------------------
# PAGE 2: 10 SQL BUSINESS QUERIES
# ---------------------------------------------------------
elif page == "🗄️ 10 SQL Business Queries":
    st.markdown('<div class="main-header">🗄️ SQL Business Insights Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Select any of the 10 SQL views to inspect the exact query logic and live dataset output.</div>', unsafe_allow_html=True)

    queries = {
        "1. Retrieve all successful bookings": (
            "SELECT * FROM ola_rides WHERE Booking_Status = 'Success';",
            df[df["Booking_Status"] == "Success"]
        ),
        "2. Find the average ride distance for each vehicle type": (
            "SELECT Vehicle_Type, ROUND(AVG(Ride_Distance), 2) AS Avg_Distance FROM ola_rides GROUP BY Vehicle_Type;",
            df.groupby("Vehicle_Type", as_index=False)["Ride_Distance"].mean().round(2).rename(columns={"Ride_Distance": "Avg_Distance"})
        ),
        "3. Get the total number of cancelled rides by customers": (
            "SELECT COUNT(*) AS Customer_Canceled_Count FROM ola_rides WHERE Booking_Status = 'Canceled by Customer';",
            pd.DataFrame({"Customer_Canceled_Count": [len(df[df["Booking_Status"] == "Canceled by Customer"])]})
        ),
        "4. List the top 5 customers who booked the highest number of rides": (
            "SELECT Customer_ID, COUNT(Booking_ID) AS Total_Rides FROM ola_rides GROUP BY Customer_ID ORDER BY Total_Rides DESC LIMIT 5;",
            df.groupby("Customer_ID", as_index=False)["Booking_ID"].count().rename(columns={"Booking_ID": "Total_Rides"}).sort_values(by="Total_Rides", ascending=False).head(5)
        ),
        "5. Get the number of rides cancelled by drivers due to personal and car-related issues": (
            "SELECT COUNT(*) AS Driver_Canceled_Personal_Car FROM ola_rides WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';",
            pd.DataFrame({"Driver_Canceled_Personal_Car": [len(df[df["Canceled_Rides_by_Driver"] == "Personal & Car related issue"])]})
        ),
        "6. Find the maximum and minimum driver ratings for Prime Sedan bookings": (
            "SELECT MAX(Driver_Ratings) AS Max_Driver_Rating, MIN(Driver_Ratings) AS Min_Driver_Rating FROM ola_rides WHERE Vehicle_Type = 'Prime Sedan';",
            pd.DataFrame({
                "Max_Driver_Rating": [df[df["Vehicle_Type"] == "Prime Sedan"]["Driver_Ratings"].max()],
                "Min_Driver_Rating": [df[df["Vehicle_Type"] == "Prime Sedan"]["Driver_Ratings"].min()]
            })
        ),
        "7. Retrieve all rides where payment was made using UPI": (
            "SELECT * FROM ola_rides WHERE Payment_Method = 'UPI';",
            df[df["Payment_Method"] == "UPI"]
        ),
        "8. Find the average customer rating per vehicle type": (
            "SELECT Vehicle_Type, ROUND(AVG(Customer_Rating), 2) AS Avg_Customer_Rating FROM ola_rides GROUP BY Vehicle_Type;",
            df.groupby("Vehicle_Type", as_index=False)["Customer_Rating"].mean().round(2).rename(columns={"Customer_Rating": "Avg_Customer_Rating"})
        ),
        "9. Calculate the total booking value of rides completed successfully": (
            "SELECT SUM(Booking_Value) AS Total_Successful_Revenue FROM ola_rides WHERE Booking_Status = 'Success';",
            pd.DataFrame({"Total_Successful_Revenue": [df[df["Booking_Status"] == "Success"]["Booking_Value"].sum()]})
        ),
        "10. List all incomplete rides along with the reason": (
            "SELECT Booking_ID, Incomplete_Rides_Reason FROM ola_rides WHERE Incomplete_Rides = 'Yes';",
            df[df["Incomplete_Rides"] == "Yes"][["Booking_ID", "Incomplete_Rides_Reason"]]
        )
    }

    selected_q = st.selectbox("Choose a SQL Business Question:", list(queries.keys()))
    sql_code, result_df = queries[selected_q]

    st.markdown("**SQL Query Executed:**")
    st.code(sql_code, language="sql")

    st.markdown(f"**Query Output ({len(result_df):,} rows):**")
    st.dataframe(result_df.head(500), use_container_width=True)

# ---------------------------------------------------------
# PAGE 3: POWER BI DASHBOARD SHOWCASE
# ---------------------------------------------------------
elif page == "📈 Power BI Dashboard Showcase":
    st.markdown('<div class="main-header">📈 Power BI Interactive Report Showcase</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Explore all 5 views built in Power BI Desktop: Overall, Vehicle Type, Revenue, Cancellation, and Ratings.</div>', unsafe_allow_html=True)

    tab_names = ["Overall", "Vehicle Type", "Revenue", "Cancellation", "Ratings"]
    tabs = st.tabs(tab_names)
    image_files = [
        "Overall.png",
        "Vehicle_Type.png",
        "Revenue.png",
        "Cancellation.png",
        "Ratings.png"
    ]

    for tab, name, img_file in zip(tabs, tab_names, image_files):
        with tab:
            if os.path.exists(img_file):
                st.image(img_file, use_container_width=True)
            else:
                st.info(f"📸 Make sure your screenshot for **{name}** is uploaded as **`{img_file}`** in your GitHub repository!")

# ---------------------------------------------------------
# PAGE 4: INTERACTIVE RIDE EXPLORER
# ---------------------------------------------------------
elif page == "🔍 Interactive Ride Explorer":
    st.markdown('<div class="main-header">🔍 Interactive Ride Data Explorer</div>', unsafe_allow_html=True)
