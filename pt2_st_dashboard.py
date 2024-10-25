# for self (in terminal): streamlit run pt2_st_dashboard.py

import streamlit as st
import pandas as pd 
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns # for box plot
from streamlit_keplergl import keplergl_static 
from keplergl import KeplerGl
from datetime import datetime as dt 
from PIL import Image
from datetime import datetime
import seaborn as sns
from numerize import numerize
import plotly.express as px


########################### IMPORT DATA & IMAGES ###########################

## DATA

# create under 25mB versions for multiple df being used in the page
#df = pd.read_csv("reduced_data_to_plot_7.csv", index_col = 0) # use for ALL

df_condensed = pd.read_csv("Citi_Weather_Date.csv") # for dual axis (11 Kb)

top20 = pd.read_csv("top20.csv", index_col = 0) # for bar (611 B)
bottom20 = pd.read_csv("bottom20.csv", index_col = 0)

df_member = pd.read_csv("member_casual_trip_bike_type.csv", low_memory=False, index_col = 0) # used for member plot, but can also be used to compare electric vs regular bikes, do filter?? (1.6 GB)


## IMAGES
citi_city = Image.open("citi_bike_city.jpg") # Photo by Anthony Fomin on Unsplash
bike_friends = Image.open("citi_friends.png") # Photo edited, but sourced from www.nysenate.gov website
bike_icon = Image.open("bike_blue.png") # Sourced from Flaticon

####################### DEFINE THE PAGES ##########################

### Dropdown Menu
st.set_page_config(initial_sidebar_state="collapsed")
page = st.sidebar.selectbox("Select an aspect of the analysis",
   ["Introduction",  "Temperature and Bike Rides", "Top 20 Most and Least Popular Stations", "Member vs Casual Comparison", "Interactive map with aggregated bike trips", "Recommendations"]) 

### Intro page
if page == "Introduction":
    col1, col2, col3 = st.columns([0.1, 0.9, 0.1],gap="small",vertical_alignment="center")
    with col1:
        st.image(bike_icon)
    with col2:
        st.header("About This Website") 
    with col3:
        st.image(bike_icon)
    st.markdown("Citi Bike is a public bicycle sharing system serving the New York City boroughs. This dashboard aims at providing helpful insights on Citi Bike By analyzing data from 2022.")
    st.markdown("New York City is the most populated city in the United States of America. This means that their consumer base is much larger than other cities; therefore, there are always avenues for expansion. With the use of several different graphs, we can notice patterns, and aim to boost sales during troughs or gaps in the market. This dashboard is separated into five sections:")
    st.markdown("- Most popular stations")
    st.markdown("- Member vs Casual Comparsion")
    st.markdown("- Weather component and bike usage")
    st.markdown(" - Interactive map with aggregated bike trips")
    st.markdown(" - Recommendations")
    st.markdown("These pages can be navigated through from the drop-down menu on the left.")
    st.image(citi_city)

### TEMP AND RIDES
elif page == "Temperature and Bike Rides":
    # Include comparison models for member vs casual, and both for temperature chart
    # function that sorts seasons 
    def pickSeason(dateStr):
        date = datetime.strptime(dateStr, "%Y-%m-%d")
        if datetime.strptime("2022-03-19", "%Y-%m-%d") >= date > datetime.strptime("2022-01-01", "%Y-%m-%d"):
            return "Winter"
        elif datetime.strptime("2022-06-20", "%Y-%m-%d") >= date > datetime.strptime("2022-03-19", "%Y-%m-%d"):
            return "Spring"
        elif datetime.strptime("2022-09-22", "%Y-%m-%d") >= date > datetime.strptime("2022-06-20", "%Y-%m-%d"):
            return "Summer"
        elif datetime.strptime("2022-12-21", "%Y-%m-%d") >= date > datetime.strptime("2022-06-20", "%Y-%m-%d"):
            return "Fall"
        else: # reminder of year is winter
            return "Winter"
            
    df_condensed["season"] = df_condensed["date"].apply(pickSeason)
    
    # adding season filter to sidebar
    with st.sidebar:
         season_filter = st.multiselect(label= "Select the season", options=df_condensed["season"].unique(), default=df_condensed["season"].unique())
    df1 = df_condensed.query("season == @season_filter")
    total_rides = float(df1["bike_rides_daily"].sum())
    # add when change df source    
    #member_filter = st.multiselect(label= "Select member status", options=df_member["member_casual"].unique(), default=df_member["member_casual"].unique()) 
    #df1 = df_member.query("member_casual == @ member_filter")

    # header of the page
    col1, col2, col3 = st.columns([0.1, 0.9, 0.1], gap="small",vertical_alignment="center")
    with col1:
        st.image(bike_icon)
    with col2:
        st.header("Weather component and bike usage") 
    with col3:
        st.image(bike_icon)
    
    # dual axis line chart
    fig = make_subplots(specs = [[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x = df1["date"], y = df1["bike_rides_daily"], name = "Daily bike rides", marker={"color": df1["bike_rides_daily"],"color": "#0e468c"}), secondary_y = False)
    fig.add_trace(
        go.Scatter(x=df1["date"], y = df1["avgTemp"], name = "Daily temperature", 
        marker={"color": df1["avgTemp"],"color": "#7ea9de"}), # made a lighter tint of blue
        secondary_y=True
    )
    fig.update_layout(
        title = "Temperature and Bike Rides",
    )
    st.plotly_chart(fig, use_container_width = True)
    
    st.metric(label = "Total Bike Rides", value = numerize.numerize(total_rides))

    st.markdown("Use the sidebar to use the seasons filter to view the data for specific seasons.")
    st.markdown("There is a positive correlation between bike usage and temperature and frequency of bike trips taken daily. As well as a negative correlation as it gets colder in Fall and Winter. As temperatures plunge, so does bike usage. This insight indicates that the Citi Bike business will continue to experience a trough during the colder months every year.")
    #st.markdown("Furthermore, the temperature range is a bit smaller for casual bike riders. This is expected because they will be less committed to riding their bike in colder weather than someone willing to pay for a membership. However, the upper and lower quartile lines that define the box are comparable. The median is also not as different as expected.")

### TOP 20
elif page == "Top 20 Most and Least Popular Stations":
    col1, col2, col3 = st.columns([0.1, 0.9, 0.1], gap="small",vertical_alignment="center")
    with col1:
        st.image(bike_icon)
    with col2:
        st.header("Top 20 Most and Least Popular Stations") 
    with col3:
        st.image(bike_icon)

    # most or least 
    with st.sidebar:
         top_bottom = st.selectbox("Most or Least Popular:", ["Most", "Least"])

    if (top_bottom == "Least"):
        df = bottom20 
        fig_title = "Top 20 Least Popular Bike Stations in New York 2022"
    else:
        df = top20
        fig_title = "Top 20 Most Popular Bike Stations in New York 2022"
        
    fig = go.Figure (
        go.Bar(
            x = df["start_station_name"], 
            y = df["value"], 
            marker={"color":df["value"], 
            "colorscale" : "Blues"}
        )
    )
    fig.update_layout(
        title = fig_title,
        xaxis_title = "Start station", 
        yaxis_title = "Sum of trips",
        width = 900, 
        height = 600
    )
    st.plotly_chart(fig, use_container_width=True)  
    st.markdown("From the bar chart it is clear that there are some start stations that are more popular than others. In the top 3, there is W 21 St & 6 Ave, West St & Chambers St, Broadway & W 58th St. This can be cross referenceed with the interactive map that is accessable through the sidebar.")
    st.markdown("The top stations likely account for a majority of the revune given the large number of tops started from this stations. Therefore, it is important that they be well-mantained and stocked.")

### MEMEBR BOX PLOT
elif page == "Member vs Casual Comparison":
    # .groupby("member_casual")["trips"].count()
    # plot that! 
    col1, col2, col3 = st.columns([0.1, 0.9, 0.1], gap="small",vertical_alignment="center")
    with col1:
        st.image(bike_icon)
    with col2:
        st.header("Member vs Casual Comparison")
    with col3:
        st.image(bike_icon)

    df_member = df_member.reset_index()
    
    with st.sidebar:
       chart_member_selection = st.sidebar.selectbox("Select Regular or Electic Bike:", ["All Bikes", "Electric Bike", "Classic Bike"])

    if (chart_member_selection == "Electric Bike"):
        df_plot = df_member[df_member["rideable_type"] == "electric_bike"] 
    elif (chart_member_selection == "Classic Bike"):
        df_plot = df_member[df_member["rideable_type"] == "classic_bike"]
    else:
        df_plot = df_member
    # else if changes df, plot is the small

    fig = px.bar(df_plot, y="trips", x = "member_casual", color = "rideable_type", title="Status vs Trips", labels= {
        "member_casual" : "Member Status",
        "trips" : "Trips",
        "rideable_type" : "Rideable Type",
    })
    st.plotly_chart(fig, use_container_width=True) 

    st.markdown("Use the sidebar to filter electric vs classic bike use across member and non-member users of Citi Bike.")
    st.markdown("Clearly, there is a larger demand for classic bikes over electric, meaning Citi Bike should focus on the maintenance and stock of non-electric bikes.")
    st.markdown("Members have a significantly higher ride count than causal users of Citi Bike, so much so that there is no overlap. Therefore, Citi Bike should prioritize keeping members. It may also be beneficial to convert casual users to members; however, that would involve figuring out if less frequent users would commit to a membership for a long period, or if their lack of frequent use would cause them to cancel the membership.")

### KELPER MAP
elif page == "Interactive map with aggregated bike trips":
    col1, col2, col3 = st.columns([0.1, 0.9, 0.1], gap="small",vertical_alignment="center")
    with col1:
        st.image(bike_icon)
    with col2:
        st.header("Interactive map showing aggregate bike trips over New York") 
    with col3:
        st.image(bike_icon)
    path_to_html = "Citi_Bike_Trips_Aggregated_Map.html"
    with open(path_to_html, "r") as f:
        html_data = f.read()
    st.header("Aggregated Bike Trips in New York")
    st.components.v1.html(html_data,height=1000)
    #st.markdown("Using the filter on the left hand side of the map we can check whether the most popular start stations also appear in the most popular trips.")
    #st.markdown("The most popular start stations are W 21 St & 6 Ave, West St & Chambers St, Broadway & W 58th St, 6 Ave & W 33 St, 1 Ave & 33 St, Broadway & E 14 St, Broadway & E 25, University Pl & 14 St, Broadway & 21 St, W 31 St & 7 Ave, E 33 St & 1 Ave.") 
    st.markdown("The most common routes, station connections that have >2700 trips, are North Moore St & Greenwich St to Vesey St & Church St, Yankee Ferry Terminal to Soissons Landing, 5 Ave & E 87 St to 5 Ave & E 87 St, West St & Chambers St to Pier 40 - Hudson River Park, and West Drive & Prospect Park West to West Drive & Prospect Park West.") 
    

### CONCLUSION
else:
    col1, col2, col3 = st.columns([0.1, 0.9, 0.1], gap="small",vertical_alignment="center")
    with col1:
        st.image(bike_icon)
    with col2:
        st.header("Conclusion and recommendations")
    with col3:
        st.image(bike_icon) 
    st.markdown("Our analysis has shown that Citi Bikes should focus on the following objectives moving forward:") 
    st.subheader("Bikes in Fall and Winter Months")
    st.markdown("There is a dip in bike rentals in the colder months; winter and fall. I would advise Citi Bike to offer a seasonal promotion, promotional discount or offer. In addition, advertisements can work alongside the promotion, where imagery can show customers riding through the autumn leaves or snow. The combination of the two could encourage casual users to becoming members, boosting citibike in the short term.")
    st.subheader("Expansion in Queens and Brooklyn")
    st.markdown("A majority of rides are focused in Manhattan, generally in Midtown and the Upper East and West side. However, Queens and Brooklyn are lacking in stations, comparatively. While it is not realistic to give Queens and Brooklyn the same density of Citi Bikes stations in NYC, there should be more. On the interactive map, Queens has routes near the water. This is a good indicator for interest. Comparative to Manhattan, the other boroughs have far fewer train lines. There is a greater reliance on buses or cars for transportation. I have observed the use of alternative transportation, like bikes, scooters, skateboards, and rollerblades have noticeable popularity in the Bronx, Queens, and Brooklyn. There are likely people who can ride bikes but don’t currently have a working bike, or don’t want to worry about maintenance or theft. This is the market for Citi Bikes in Queens, Brooklyn, and the Bronx.")
    st.subheader("Supply Based on Usage")
    st.markdown("Classic Bikes are more popular, therefore production should be proportional to electric. Additionally, Classic bikes should be high in rotation amongst the top 20 stations, especially near popular biking destinations such as Central Park and the Hudson River, along with popular worker commuter destinations such as Midtown.")
    st.image(bike_friends)
    
