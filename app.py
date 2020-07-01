import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

st.title('Collisions Data of NewYork City')
st.markdown('## New York Collisions Data Web App')

st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv('collisions_data.csv',nrows=nrows,parse_dates=[['CRASH DATE','CRASH TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'],inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase,axis='columns',inplace=True)
    data.rename(columns={'crash date_crash time':'date/time'},inplace=True)
    return data

data  = load_data(10000)
original_data = data
print(original_data.columns)
st.header('Where are the most people injured in NYC ?')
injured_people = st.slider("Number of People Injured",0,19)
st.map(data.query(" injured_persons >= @injured_people")[['latitude','longitude']].dropna(how="any"))

st.header('How many collisions has occured in a given time of date ?')
hour = st.slider("Hour to look at", 0,23)
data = data[data['date/time'].dt.hour == hour]

st.markdown('Vehicle collisions between %i:00 and %i:00' % (hour,(hour+1) % 24))
midpoint = (np.average(data['latitude']),np.average(data['longitude']))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude":midpoint[0],
        "longitude":midpoint[1],
        "zoom":11,
        "pitch":50
    },
    layers=[        
        pdk.Layer(
        "HexagonLayer",
        data=data[['date/time','latitude','longitude']],
        get_position = ['longitude','latitude'],
        radius = 100,
        extruded=True,
        pickable=True,
        elevation_scale=4,
        elevation_range=[0,1000],
        ),
    ],
))

st.subheader('Breakdown by minute between %i:00 and %i:00' % (hour,(hour + 1) % 24))

filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]

hist = np.histogram(filtered['date/time'].dt.minute,bins=60,range=(0,60))[0]
chart_data = pd.DataFrame({'minute':range(60),'crashes':hist})
fig = px.bar(chart_data,x='minute',y='crashes',hover_data=['minute','crashes'],height=400)
st.write(fig)

st.header('Top 5 dangerous streets by affected type')
select = st.selectbox('Affected type of people',['Pedestrians','Cyclists','Motorists'])
if select == 'Pedestrians':
    st.write(original_data[original_data['number of pedestrians injured'] >= 1][['on street name','number of pedestrians injured']]
            .sort_values(by=['number of pedestrians injured'],ascending=False)
            .dropna(how='any')[:5])

elif select == 'Cyclists':
    st.write(original_data[original_data['number of cyclist injured'] >= 1][['on street name','number of cyclist injured']]
            .sort_values(by=['number of cyclist injured'],ascending=False)
            .dropna(how='any')[:5])

else:
    st.write(original_data[original_data['number of motorist injured'] >= 1][['on street name','number of motorist injured']]
            .sort_values(by=['number of motorist injured'],ascending=False)
            .dropna(how='any')[:5])

if st.checkbox("Show Raw Data",False):
    st.subheader('Raw Data')
    st.write(data)