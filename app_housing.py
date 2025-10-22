import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Housing Data App", layout="wide")
st.title("California Housing Data(1990) by Yujia He")
st.markdown("Explore the housing dataset by filtering with price, location type, and income level, and visualize the spatial and value distributions.")

@st.cache_data
def load_data(path="housing.csv"):
    df = pd.read_csv(path)
    expected = {"longitude", "latitude", "median_house_value", "median_income", "ocean_proximity"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    df = df.dropna(subset=["longitude", "latitude", "median_house_value", "median_income", "ocean_proximity"])
    return df

try:
    data = load_data("housing.csv")
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

st.sidebar.header("Filter Options")

locations = sorted(data["ocean_proximity"].unique())
selected_locations = st.sidebar.multiselect("Select location type", options=locations, default=locations)

st.sidebar.markdown("Filter by median income level:")
income_choice = st.sidebar.radio(
    "Select income level",
    options=["All", "Low (< 2.5)", "Medium (2.5 - < 4.5)", "High (>= 4.5)"],
    index=0
)

min_price = int(data["median_house_value"].min())
max_price = int(data["median_house_value"].max())
price_min, price_max = st.sidebar.slider(
    "Median house value range",
    min_value=0,
    max_value=500000,
    value=(min_price, max_price),
    step=1000
)

st.sidebar.markdown("---")
st.sidebar.write("Total records in dataset:", len(data))

df_filtered = data.copy()

if selected_locations:
    df_filtered = df_filtered[df_filtered["ocean_proximity"].isin(selected_locations)]
else:
    st.warning("No location type selected. Please select at least one option.")
    st.stop()

if income_choice == "Low (< 2.5)":
    df_filtered = df_filtered[df_filtered["median_income"] < 2.5]
elif income_choice == "Medium (2.5 - < 4.5)":
    df_filtered = df_filtered[(df_filtered["median_income"] >= 2.5) & (df_filtered["median_income"] < 4.5)]
elif income_choice == "High (>= 4.5)":
    df_filtered = df_filtered[df_filtered["median_income"] >= 4.5]


df_filtered = df_filtered[(df_filtered["median_house_value"] >= price_min) & (df_filtered["median_house_value"] <= price_max)]

st.subheader("See more filters in the sidebar:")

if not df_filtered.empty:
    st.map(df_filtered[["latitude", "longitude"]])
else:
    st.info("No data available for the current filter conditions.")

st.subheader("Distribution of Median House Value (30 bins)")
fig, ax = plt.subplots(figsize=(8, 5))
if not df_filtered.empty:
    ax.hist(df_filtered["median_house_value"], bins=30)
    ax.set_xlim()  
    ax.set_ylim()
    ax.set_xlabel("Median House Value",fontsize=11)
    ax.set_ylabel("Frequency",fontsize=11)
    ax.set_title("Median House Value Distribution (30 bins)",fontsize=13)
    st.pyplot(fig)
else:
    ax.text(0.5, 0.5, "No data", ha="center", va="center", fontsize=14)
    ax.set_axis_off()
    st.pyplot(fig)

st.subheader("Filtered Data Overview")
st.write(f"Number of records after filtering: {len(df_filtered)}")
st.dataframe(df_filtered.head(50))

st.subheader("Key Statistics")
if not df_filtered.empty:
    stats = df_filtered[["median_house_value", "median_income"]].agg(
        ["count", "mean", "std", "min", "median", "max"]
    ).T
    stats = stats.rename(
        columns={
            "count": "Count",
            "mean": "Mean",
            "std": "Std Dev",
            "min": "Min",
            "median": "Median",
            "max": "Max",
        }
    )
    st.table(stats)
else:
    st.write("No statistics available.")