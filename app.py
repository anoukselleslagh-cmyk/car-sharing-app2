import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Car Sharing Dashboard",
    page_icon="🚗",
    layout="wide"
)

# ── Data Loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    trips     = pd.read_csv("datasets/trips.csv")
    cars      = pd.read_csv("datasets/cars.csv")
    customers = pd.read_csv("datasets/customers.csv")
    ratings   = pd.read_csv("datasets/ratings.csv")
    cities    = pd.read_csv("datasets/cities.csv")

    trips["pickup_time"]  = pd.to_datetime(trips["pickup_time"])
    trips["dropoff_time"] = pd.to_datetime(trips["dropoff_time"])
    trips["pickup_date"]  = trips["pickup_time"].dt.date
    trips["month"]        = trips["pickup_time"].dt.to_period("M").astype(str)

    # Enrich trips
    merged = (
        trips
        .merge(cars[["id", "brand", "model", "year", "daily_price", "city_id"]],
               left_on="car_id", right_on="id", how="left")
        .merge(cities, on="city_id", how="left")
        .merge(ratings[["trip_id", "rating"]], left_on="id_x", right_on="trip_id", how="left")
    )
    return trips, cars, customers, ratings, cities, merged

trips, cars, customers, ratings, cities, merged = load_data()

# ── Sidebar Filters ───────────────────────────────────────────────────────────
st.sidebar.title("🔧 Filters")

all_cities  = sorted(cities["city_name"].dropna().unique())
all_brands  = sorted(cars["brand"].dropna().unique())

sel_cities = st.sidebar.multiselect("City", all_cities, default=all_cities)
sel_brands = st.sidebar.multiselect("Car Brand", all_brands, default=all_brands)

min_date = trips["pickup_time"].min().date()
max_date = trips["pickup_time"].max().date()
date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date),
                                    min_value=min_date, max_value=max_date)

# Apply filters
df = merged.copy()
if sel_cities:
    df = df[df["city_name"].isin(sel_cities)]
if sel_brands:
    df = df[df["brand"].isin(sel_brands)]
if len(date_range) == 2:
    df = df[(df["pickup_time"].dt.date >= date_range[0]) &
            (df["pickup_time"].dt.date <= date_range[1])]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🚗 Car Sharing Analytics Dashboard")
st.markdown("Explore operational data across cities, car brands, trips, and revenue.")

# ── KPI Metrics ───────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Trips",            f"{len(df):,}",                  border=True)
k2.metric("Total Revenue",          f"€{df['revenue'].sum():,.0f}",   border=True)
k3.metric("Avg Revenue / Trip",     f"€{df['revenue'].mean():.2f}",   border=True)
k4.metric("Total Distance (km)",    f"{df['distance'].sum():,.0f}",   border=True)
avg_rating = df["rating"].mean()
k5.metric("Avg Rating",             f"{avg_rating:.2f} ⭐" if not pd.isna(avg_rating) else "N/A", border=True)

st.divider()

# ── Row 1 ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Revenue Over Time")
    rev_time = df.groupby("month")["revenue"].sum().reset_index()
    rev_time.columns = ["Month", "Revenue"]
    fig = px.line(rev_time, x="Month", y="Revenue", markers=True,
                  color_discrete_sequence=["#1f77b4"])
    fig.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🏙️ Trips by City")
    city_trips = df["city_name"].value_counts().reset_index()
    city_trips.columns = ["City", "Trips"]
    fig2 = px.bar(city_trips, x="City", y="Trips", color="City",
                  color_discrete_sequence=px.colors.qualitative.Set2)
    fig2.update_layout(showlegend=False, margin=dict(t=20, b=20))
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2 ─────────────────────────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("🚘 Revenue by Car Brand")
    brand_rev = df.groupby("brand")["revenue"].sum().sort_values(ascending=False).reset_index()
    brand_rev.columns = ["Brand", "Revenue"]
    fig3 = px.bar(brand_rev, x="Revenue", y="Brand", orientation="h",
                  color="Revenue", color_continuous_scale="Blues")
    fig3.update_layout(margin=dict(t=20, b=20), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("⭐ Rating Distribution")
    rat_dist = df["rating"].dropna().value_counts().sort_index().reset_index()
    rat_dist.columns = ["Rating", "Count"]
    fig4 = px.bar(rat_dist, x="Rating", y="Count",
                  color_discrete_sequence=["#f5a623"])
    fig4.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3 ─────────────────────────────────────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.subheader("📊 Trips by Car Brand")
    brand_trips = df["brand"].value_counts().reset_index()
    brand_trips.columns = ["Brand", "Trips"]
    fig5 = px.pie(brand_trips, names="Brand", values="Trips",
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    fig5.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.subheader("💰 Avg Revenue by City")
    city_avg = df.groupby("city_name")["revenue"].mean().sort_values(ascending=False).reset_index()
    city_avg.columns = ["City", "Avg Revenue"]
    fig6 = px.bar(city_avg, x="City", y="Avg Revenue", color="Avg Revenue",
                  color_continuous_scale="Greens")
    fig6.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig6, use_container_width=True)

# ── Map ───────────────────────────────────────────────────────────────────────
st.subheader("🗺️ Pickup Locations")
map_df = df[["pickup_lat", "pickup_lon"]].dropna().sample(min(2000, len(df)), random_state=42)
map_df.columns = ["lat", "lon"]
st.map(map_df, size=10)

# ── Raw Data ──────────────────────────────────────────────────────────────────
with st.expander("🔍 View Raw Data"):
    st.dataframe(df[["id_x", "pickup_time", "dropoff_time", "distance",
                      "revenue", "brand", "model", "city_name", "rating"]].head(200),
                 use_container_width=True)
