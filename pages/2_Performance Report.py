import os
import sqlite3
import datetime as dt
import requests
import pandas as pd

import streamlit as st
import streamlit_extras
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit_lottie import st_lottie

st.set_page_config(page_title='JSAX Trade',
                   layout='wide',
                   page_icon='https://jsax.notion.site/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2Fba07c969-ad44-4ac9-b475-1585436607ee%2FUntitled.png?table=block&id=8570f62a-2323-4bbd-ba98-e9043c3fa20b&spaceId=a34bbc1a-8979-401d-ac95-4dc80e288722&width=2000&userId=&cache=v2')
from streamlit_extras.app_logo import add_logo
from streamlit_extras.dataframe_explorer import dataframe_explorer

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
base_url = "https://raw.githubusercontent.com/jsacap/jsax-trade-floor/master/"
csv_url = base_url + "trades.csv"
db_url = base_url + "trades.db"
db_filename = 'trades.db'
db_path = os.path.abspath(db_filename)

def load_data():
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
    else:
        conn = sqlite3(db_url)
    query = "SELECT * FROM trades"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

df = load_data()

 

# Convert to date
df['Date'] = pd.to_datetime(df['Date'])
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

st.write(f"""
Welcome to the performance report. This report is automatically generated by pulling trades from the database, dissecting the information, and presenting it in a readable format for traders to understand.

The report is divided into multiple sections to provide a detailed analysis of trade statistics. This analysis can help identify patterns for us to exploit and improve our trading edge.

                           
""")

# Prepping the choices for months
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
df['Month'] = df['Date'].dt.strftime('%B %Y')
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
overall_r = selected_df['R'].sum()
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


#Overall report
# if selected_month == 'Overall Performance':
st.write(f"""
    # Overview
    This is the {selected_month} report.
    The total gain (in R multiple) in the course of the entire trading performance from the trades in tracked from the database is {overall_r}. 
    During this period, the largest drawdown experienced was at {largest_drawdown}.
    The strongest trade was the {top_asset} returning a total of {top_asset_r}! 
    This was executed through a {top_wins['System Strategy'].values[0]} entering at
    the {top_wins['Trade From'].values[0]} structure.
    Trades executed during the {top_session} session has been most prfitable 
    returning a total of {top_session_r}R whereas the weakest session was the 
    {trading_session_r.index[2]} with a return of {trading_session_r.values[2]}. 
    Trades during the {trading_session_r.index[1]} came in at second returning {trading_session_r.values[1]}R.
    Here are a couple charts to plot the overview.
""")
    
# Plotting the overview chart
def plot_rolling_r():
    fig = px.line(selected_df, x='Trade ID', y='Rolling R', title='R CUrve')
    fig.update_layout(plot_bgcolor='#0a0a0a')
    st.plotly_chart(fig)

def plot_asset_r():
    fig = px.bar(asset_r, x='Asset', y='R', title='Asset Traded Based Returns')
    fig.update_layout(plot_bgcolor='#0a0a0a')
    st.plotly_chart(fig)

col1, col2 = st.columns(2)
with col1:
    plot_rolling_r()
with col2:
    plot_asset_r()


# Variables used for the Trade Type section
trade_type = df.groupby('Trade Type')['R'].sum().sort_values(ascending=False).reset_index()
trade_type_list = [trade_type_name.title() for trade_type_name in trade_type['Trade Type']]
trade_type_string = ', '.join(trade_type_list)
trade_type_1 = trade_type['Trade Type'].iloc[0]
trade_type_2 = trade_type['Trade Type'].iloc[1]
trade_type_3 = trade_type['Trade Type'].iloc[2]
trade_type1_df = df[df['Trade Type'] == trade_type_1]
trade_type2_df = df[df['Trade Type'] == trade_type_2]
trade_type3_df = df[df['Trade Type'] == trade_type_3]
# trade_type1_df = trade_type1_df.groupby(['Asset', 'System Strategy', 'Trade From'])['R'].sum().sort_values(ascending=False).reset_index()
trade_type1_asset = trade_type1_df.groupby('Asset')['R'].sum().sort_values(ascending=False).reset_index()
trade_type1_system = trade_type1_df.groupby('System Strategy')['R'].sum().sort_values(ascending=False).reset_index()
trade_type1_tradefrom = trade_type1_df.groupby('Trade From')['R'].sum().sort_values(ascending=False).reset_index()
st.write(f"""
# Diving Deeper
Let's take a deep dive into the stats to gain more valuable insights.
         
## Who, What & Where
         This section will run through the who(Assets), the what(Strategies), and
         where (structure of where the trade was taken).
The total number of trade types in the trading data is {len(trade_type)}:
 {trade_type_string}. With each of these trade types this is how they 
performed: 
- The strongest one being {trade_type['Trade Type'].iloc[0]} returning 
a total of {trade_type['R'].iloc[0]}R. 
- Followed by {trade_type['Trade Type'].iloc[1]}
 returning a total of {trade_type['R'].iloc[1]} 
 - Lastly, the {trade_type['Trade Type'].iloc[2]}
 with a return of {trade_type['R'].iloc[2]}.
 

 ### {trade_type['Trade Type'].iloc[0].title()}
Starting witht the top of the list and working our way down we can take a better
look at which type of {trade_type['Trade Type'].iloc[0]} trades worked best
with different setups and where they were traded from. Filtering the data
I will present this through the dataframe itself, followed by a couple plots to 
visualise our data. I have listed the tables below that describe each of the 
variables in the execution of the {trade_type_1} trade3
The {trade_type_1.title()} setups accu,accumulated a total return of {trade_type1_df['R'].sum()}R.

""")

# Charting the data

def plot_trade_type1_asset():
    fig = px.scatter(trade_type1_asset, x='Asset', y='R', 
                     height=400, title='Asset Scatter Plot')
    st.plotly_chart(fig)

def plot_trade_type2_asset():
    fig = px.scatter(trade_type2_asset, x='Asset', y='R', 
                     height=400, title='Asset Scatter Plot')
    st.plotly_chart(fig)

def plot_trade_type1_system():
    fig = px.bar(trade_type1_system, x='R', y='System Strategy', orientation='h',
                 title=f'{trade_type_1} Strategy Performance')
    st.plotly_chart(fig)

def plot_trade_type1_positive():
    positive_df = trade_type1_df[trade_type1_df['R'] >= 0]
    fig_positive = px.scatter_3d(positive_df, x='Asset', y='System Strategy', z='Trade From', 
                            color='R', color_continuous_scale='Viridis', opacity=0.7, 
                            title='Scatter Plot based on Winning Trades')
    fig_positive.update_layout(scene=dict(bgcolor='#0a0a0a'))
    st.plotly_chart(fig_positive)


def plot_trade_system_pie():
    positive_df = trade_type1_df[trade_type1_df['R'] >= 0]
    fig = px.pie(positive_df, values='R', names='Asset', title='Profitable Assets Traded')
    color_scale = px.colors.sequential.Viridis  # You can use any color scale
    fig.update_traces(marker=dict(colors=color_scale))
    st.plotly_chart(fig)

def plot_system_bar():
    positive_df = trade_type1_df[trade_type1_df['R'] >= 0]
    fig = px.bar(positive_df, x='R', y='System Strategy', orientation='h')

    st.plotly_chart(fig)

# Plotting 
trade_type1_df

col3, col4, col5 = st.columns([1, 3, 3])
with col3:
    trade_type1_asset
with col4:
    # plot_trade_type1_asset()
    st.bar_chart(trade_type1_asset, x='Asset', y='R')
with col5:
    plot_trade_type1_asset()

col6, col7, col8 = st.columns([1, 3, 3])
with col6:
    trade_type1_system
with col7:
    st.bar_chart(trade_type1_system, x='System Strategy', y='R', height=400)
with col8:
    st.area_chart(trade_type1_system, x='R', y='System Strategy')

col9, col10, col11 = st.columns([1, 3, 3])
with col9:
    trade_type1_tradefrom
with col10:
    st.bar_chart(trade_type1_tradefrom, x='R', y='Trade From')
with col11:
    st.area_chart(trade_type1_tradefrom, x='Trade From', y='R')

st.write(f"""
### {trade_type_2.title()}
Next on the list of trades to analyse is the {trade_type_2.title()}. These types of
trades closed at a total R of {trade_type2_df['R'].sum()}. The top performer here was 
the 
{trade_type1_df.groupby('Asset').sum().sort_values(by='R', ascending=False).reset_index().iloc[0]['Asset']}
which returned a total of 
{trade_type1_df.groupby('Asset').sum().sort_values(by='R', ascending=False).reset_index().iloc[0]['R']}
On the flipside, the weakest performing asset was the
{trade_type1_df.groupby('Asset').sum().sort_values(by='R', ascending=False).reset_index().iloc[-1]['Asset']}
which closed at 
{trade_type1_df.groupby('Asset').sum().sort_values(by='R', ascending=False).reset_index().iloc[-1]['R']}
Now, to visualise our data, we will be plotting the same charts as we did in the 
{trade_type_1} section.
""")

# Variables for next section
trade_type2_asset = trade_type1_df.groupby('Asset')['R'].sum().sort_values(ascending=False).reset_index()
trade_type2_system = trade_type1_df.groupby('System Strategy')['R'].sum().sort_values(ascending=False).reset_index()
trade_type2_tradefrom = trade_type1_df.groupby('Trade From')['R'].sum().sort_values(ascending=False).reset_index()

# Charting

# Plotting 
trade_type2_df

col12, col13, col14 = st.columns([1, 3, 3])
with col12:
    trade_type2_asset
with col13:
    # plot_trade_type2_asset()
    st.bar_chart(trade_type2_asset, x='Asset', y='R')
with col14:
    plot_trade_type2_asset()

col15, col16, col17 = st.columns([1, 3, 3])
with col15:
    trade_type2_system
with col16:
    st.bar_chart(trade_type2_system, x='System Strategy', y='R', height=400)
with col17:
    st.area_chart(trade_type2_system, x='R', y='System Strategy')

col18, col19, col20 = st.columns([1, 3, 3])
with col18:
    trade_type2_tradefrom
with col19:
    st.bar_chart(trade_type2_tradefrom, x='R', y='Trade From')
with col20:
    st.area_chart(trade_type2_tradefrom, x='Trade From', y='R')