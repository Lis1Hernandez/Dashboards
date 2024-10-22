# to run: streamlit run st_dashboard.py

import streamlit as st
import pandas as pd 
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from streamlit_keplergl import keplergl_static 
from keplergl import KeplerGl
from datetime import datetime as dt 

st.set_page_config(page_title = "Citi Bikes Strategy Dashboard", layout="wide")
st.title("Citi Bikes Strategy Dashboard")
st.markdown("The dashboard will help with the anaylsis Citi Bike usage to give insight into the success and failings of the business.")

############################ CHART DEFINITIONS ############################

## read in data
df = pd.read_csv("reduced_data_to_plot.csv", index_col = 0)
top20 = pd.read_csv("top20.csv", index_col = 0)

## top 20 bar
fig = go.Figure(go.Bar(x = top20["start_station_name"], y = top20["value"], marker = {"color" : top20["value"], "colorscale" : "PuRd"}))
fig.update_layout(
    title = "Top 20 Most Popular Citi Bike Stations in New York 2024",
    xaxis_title = "Start Stations", 
    yaxis_title = "Sum of Trips", 
    width = 900, height = 600
)
st.plotly_chart(fig, use_container_width = True)

## dual axis plot
df_condensed = pd.read_csv("Citi_Weather_Date")
fig = make_subplots(specs = [[{"secondary_y": True}]])
fig.add_trace(
 go.Scatter(x = df_condensed["date"], y = df_condensed["bike_rides_daily"], name = "Daily bike rides", 
 marker={"color": df_condensed["bike_rides_daily"],"color": "#dd1c77"}),
 secondary_y = False)
fig.add_trace(
 go.Scatter(x=df_condensed["date"], y = df_condensed["avgTemp"], name = "Daily temperature", 
 marker={"color": df_condensed["avgTemp"],"color": "#61187c"}),
 secondary_y=True)
fig.update_layout(
    title = "Citi Bike Rides vs Temperature in New York 2024",
    xaxis_title = "Start stations",
    yaxis_title ="Sum of trips",
    width = 900, height = 600)
st.plotly_chart(fig, use_container_width = True)

############################ IMPORT & DISPLAY MAP ############################

## read in map
path_to_html = "Citi_Bike_Trips_Aggregated_Map.html"
with open(path_to_html, "r") as f:
    html_data = f.read()

## display
st.header("Aggregated Top Citi Bike Trips in New York 2024")
st.components.v1.html(html_data,height = 1000)