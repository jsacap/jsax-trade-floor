import os
import sqlite3
import calendar
import datetime as dt
import requests
import pandas as pd
import matplotlib.pyplot as plt


import streamlit as st
import streamlit_extras
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit_lottie import st_lottie

st.set_page_config(page_title='JSAX Trade',
                   layout='wide',
                   page_icon='https://jsax.notion.site/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2Fba07c969-ad44-4ac9-b475-1585436607ee%2FUntitled.png?table=block&id=8570f62a-2323-4bbd-ba98-e9043c3fa20b&spaceId=a34bbc1a-8979-401d-ac95-4dc80e288722&width=2000&userId=&cache=v2')
from streamlit_extras.app_logo import add_logo
from streamlit_extras.dataframe_explorer import dataframe_explorer

@st.cache_data
def load_lottie(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_chart = load_lottie('https://lottie.host/42788987-5c50-4581-9028-8073e83c92b4/Lmu8OPV7UQ.json')
# Args for lottie - speed=*, 
    # reverse=False, loop=True, quality='low', 
    # render='sug' (canvas), height=*, width=*, key=None


# ---- Page description ----
cl1, cl2, cl3 = st.columns(3)
with cl1:
    st_lottie(lottie_chart, loop=False, speed=0.9)
with cl2:
    st.write(' ')
    st.image('https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2F8587d9d9-ebba-474d-bbe3-2220a86e95be%2FUntitled.png?table=block&id=92875c04-e03b-4599-abf2-b810d8ea04df&spaceId=a34bbc1a-8979-401d-ac95-4dc80e288722&width=2000&userId=e094dc45-70bb-460a-8bf7-97e454446eca&cache=v2', width=800)
with cl3: 
    st.write(' ')
add_logo('https://raw.githubusercontent.com/jsacap/jsax-trade-floor/master/coin_logo.png')
st.title('Performance Report')


# ---- Hide ST HTML ----
hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)


# GitHub raw content URLs
base_url = "https://github.com/jsacap/jsax-trade-floor"
csv_url = base_url + "trades.csv"
db_url = 'https://github.com/jsacap/jsax-trade-floor/raw/master/trades.db'
db_filename = 'trades.db'
db_path = os.path.abspath(db_filename)

@st.cache_data
def load_data():
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        st.write('DB local')
    else:
        conn = sqlite3.connect(db_url)
        st.write('DB', db_url)
    query = "SELECT * FROM trades"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

df = load_data()
df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.month
df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S.%f').dt.strftime('%H:%M')
df['Month'] = df['Month'].apply(lambda m: calendar.month_name[int(m)])


st.write(f"""
Welcome to the performance report. This report is automatically generated by pulling trades from the database, dissecting the information, and presenting it in a readable format for traders to understand.

The report is divided into multiple sections to provide a detailed analysis of trade statistics. This analysis can help identify patterns for us to exploit and improve our trading edge.

                           
""")

# Prepping the choices for months
available_months = df['Month'].unique()
available_months = ['Overall Performance'] + list(available_months)

# Add a multiselect to choose month of report
selected_month = st.selectbox("Select a Report", available_months)

#Filtering df acording to month selected. (Overall Performance is the entire df)
if selected_month == 'Overall Performance':
    selected_df = df
else:
    selected_df = df[df['Month'] == selected_month]

# Variables for the Overall report
overall_r = round(selected_df['R'].sum(), 2)
wins = selected_df.loc[selected_df['R'] > 0]
top_wins = wins.nlargest(3, 'R')
top_asset = top_wins['Asset'].values[0]
top_asset_r = top_wins['R'].values[0]
trading_session_r = selected_df.groupby('Trading Session')['R'].sum()
trading_session_r = trading_session_r.sort_values(ascending=False)
top_session = trading_session_r.index[0]
top_session_r = trading_session_r.values[0]
asset_r = selected_df.groupby('Asset')['R'].sum().sort_values(ascending=False).reset_index()

# Drawdown calculation
largest_drawdown = 0
peak_value = selected_df['Rolling R'].iloc[0]
for index, row in selected_df.iterrows():
    if row['Rolling R'] > peak_value:
        peak_value = row['Rolling R']
    else:
        drawdown = peak_value - row['Rolling R']
        largest_drawdown = max(largest_drawdown, drawdown)

# Metrics
# Total R, 2-Average Win R, 3-Peak Value, 4-Drawdown, 5-Profit factor
sum_positive_r = selected_df[selected_df['R'] > 0]['R'].sum()
sum_negative_r = selected_df[selected_df['R'] < 0]['R'].abs().sum()
profit_factor = round(sum_positive_r / sum_negative_r, 2)

mt1, mt2, mt3, mt4, mt5 = st.columns(5)
mt1.metric('Total Return (R)', round(selected_df['R'].sum(), 2))
mt2.metric('Avg. Winning R', round(df[df['R'] >0]['R'].mean(), 2))
mt3.metric('Peak Value', round(df['Rolling R'].max(), 2))           
mt4.metric('Max Drawdown', largest_drawdown)
mt5.metric('Profit Factor', profit_factor)

# Variables


# Charting
def plot_rollingr():
    fig = px.line(df, x='Trade ID', 
                  y='Rolling R', 
                  title='Performance',
                #   hover_data=['Asset']
                )
    st.plotly_chart(fig)


plot_rollingr

st.write(f'''
# Overview
         During this period, our trading system returned a total of 
''')