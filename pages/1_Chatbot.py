import streamlit as st
import pandas as pd

st.set_page_config(page_title="Data Chatbot", page_icon="🤖", layout="wide")

@st.cache_data
def load_data():
    trips     = pd.read_csv("datasets/trips.csv")
    cars      = pd.read_csv("datasets/cars.csv")
    customers = pd.read_csv("datasets/customers.csv")
    ratings   = pd.read_csv("datasets/ratings.csv")
    cities    = pd.read_csv("datasets/cities.csv")
    trips["pickup_time"] = pd.to_datetime(trips["pickup_time"])
    merged = (
        trips
        .merge(cars[["id", "brand", "model", "city_id"]],
               left_on="car_id", right_on="id", how="left")
        .merge(cities, on="city_id", how="left")
        .merge(ratings[["trip_id", "rating"]], left_on="id_x", right_on="trip_id", how="left")
    )
    return trips, cars, customers, ratings, cities, merged

trips, cars, customers, ratings, cities, merged = load_data()

st.title("🤖 Car Sharing Data Chatbot")
st.write("Ask me anything about the car sharing data! Try: *total revenue*, *trips by city*, *best rated brand*, *average distance*, *top brand*...")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

def answer(query: str) -> str:
    q = query.lower()

    if "total revenue" in q or "revenue total" in q:
        val = merged["revenue"].sum()
        return f"💰 Total revenue across all trips is **€{val:,.2f}**."

    if "average revenue" in q or "avg revenue" in q:
        val = merged["revenue"].mean()
        return f"💰 Average revenue per trip is **€{val:.2f}**."

    if "total trip" in q or "how many trip" in q or "number of trip" in q:
        return f"🚗 There are **{len(merged):,}** trips in the dataset."

    if "average distance" in q or "avg distance" in q:
        val = merged["distance"].mean()
        return f"📏 The average trip distance is **{val:.2f} km**."

    if "total distance" in q:
        val = merged["distance"].sum()
        return f"📏 Total distance across all trips is **{val:,.0f} km**."

    if "average rating" in q or "avg rating" in q:
        val = merged["rating"].mean()
        return f"⭐ The average customer rating is **{val:.2f} / 5**."

    if "top brand" in q or "best brand" in q or "most trip" in q:
        top = merged["brand"].value_counts().idxmax()
        cnt = merged["brand"].value_counts().max()
        return f"🏆 The top brand by number of trips is **{top}** with **{cnt:,}** trips."

    if "best rated brand" in q or "highest rated brand" in q:
        top = merged.groupby("brand")["rating"].mean().idxmax()
        val = merged.groupby("brand")["rating"].mean().max()
        return f"⭐ The highest rated brand is **{top}** with an average rating of **{val:.2f}**."

    if "trips by city" in q or "city trips" in q:
        s = merged["city_name"].value_counts()
        lines = "\n".join([f"- **{c}**: {n:,}" for c, n in s.items()])
        return f"🏙️ Trips by city:\n{lines}"

    if "revenue by city" in q or "city revenue" in q:
        s = merged.groupby("city_name")["revenue"].sum().sort_values(ascending=False)
        lines = "\n".join([f"- **{c}**: €{v:,.0f}" for c, v in s.items()])
        return f"💰 Revenue by city:\n{lines}"

    if "revenue by brand" in q or "brand revenue" in q:
        s = merged.groupby("brand")["revenue"].sum().sort_values(ascending=False).head(10)
        lines = "\n".join([f"- **{b}**: €{v:,.0f}" for b, v in s.items()])
        return f"💰 Top 10 brands by revenue:\n{lines}"

    if "how many car" in q or "number of car" in q:
        return f"🚘 There are **{len(cars):,}** cars in the fleet."

    if "how many customer" in q or "number of customer" in q:
        return f"👥 There are **{len(customers):,}** registered customers."

    if "how many cit" in q or "number of cit" in q:
        return f"🏙️ The service operates in **{len(cities)}** cities: {', '.join(cities['city_name'].tolist())}."

    if "which city" in q and "most revenue" in q:
        top = merged.groupby("city_name")["revenue"].sum().idxmax()
        val = merged.groupby("city_name")["revenue"].sum().max()
        return f"🏆 The city with the most revenue is **{top}** with **€{val:,.0f}**."

    return (
        "🤔 I didn't understand that. Try asking:\n"
        "- *total revenue* / *average revenue*\n"
        "- *total trips* / *trips by city*\n"
        "- *average distance* / *total distance*\n"
        "- *average rating* / *best rated brand*\n"
        "- *top brand* / *revenue by brand* / *revenue by city*\n"
        "- *how many cars* / *how many customers* / *how many cities*"
    )

user_query = st.chat_input("Ask a question about the data...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    response = answer(user_query)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)
