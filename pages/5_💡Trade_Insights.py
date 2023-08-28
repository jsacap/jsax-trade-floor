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
st.set_page_config(layout='wide')
from streamlit_extras.app_logo import add_logo
from streamlit_extras.dataframe_explorer import dataframe_explorer




# ---- Page description ----
cl1, cl2, cl3 = st.columns(3)
with cl1:
    st.write(' ')
with cl2:
    st.image('https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2F8587d9d9-ebba-474d-bbe3-2220a86e95be%2FUntitled.png?table=block&id=92875c04-e03b-4599-abf2-b810d8ea04df&spaceId=a34bbc1a-8979-401d-ac95-4dc80e288722&width=2000&userId=e094dc45-70bb-460a-8bf7-97e454446eca&cache=v2', width=800)

with cl3: 
    st.write(' ')
add_logo(r'C:\Users\saleg\Desktop\jupyter\Projects\JSAX_trade_floor\coin_logo.png')
st.title('💡Trade Insights')

# ---- Hide ST HTML ----

hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)


# ---- Read existing data database----
file_directory = r'C:\Users\saleg\Desktop\jupyter\Projects\JSAX_trade_floor'
db_file = os.path.join(file_directory, 'trades.db')
conn = sqlite3.connect(db_file)
query = 'SELECT * FROM trades'
df = pd.read_sql(query, conn)
conn.close()

# Case insensitive TO BE COMPLETED


# Convert to date
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')


# ---- SIDEBAR ----
st.sidebar.header('FILTER TRADES')
categories = ['Asset', 'Trade Type', 'System Strategy', 'Timeframe',
              'HTF Trend', 'Trade From', 'Day of Week', 'Direction']

multiselect_widget = {
    category: st.sidebar.multiselect(
        f'Select {category}', options=df[category].unique(), default=[])
    for category in categories

}


# --- Dictionary comprehensions to create filter conditions
filter_conditions = {
    category: df[category].isin(selected_values) for category, selected_values in multiselect_widget.items()}

# Dictionary comprehension to create filter conditions
filter_conditions = {
    category: df[category].isin(selected_values) for category, selected_values in multiselect_widget.items()
}



st.markdown('##')

# ---- Dashboard Charting----
# Check if any filters are selected
if any(selected_values for selected_values in multiselect_widget.values()):
    df_selection = df  # Initialize df_selection with the original DataFrame
    for category, selected_values in multiselect_widget.items():
        if selected_values:
            df_selection = df_selection[df_selection[category].isin(selected_values)]
else:
    df_selection = df  # Use the original DataFrame


# --- Creating groups to be used in filters
positive_r = df.loc[df['R'] > 0]
asset_r = df.groupby('Asset')['R'].sum()
asset_r_selection = df.groupby('Asset')['R'].sum().sort_values(ascending=False)
strategy_r = df.groupby('Asset')['R'].sum()

day_r = df.groupby('Day of Week')['R'].sum()
trade_from_group = df.groupby('Trade From')['R'].sum()


# Identify the top-performing asset
top_r = positive_r.nlargest(1, 'R')
top_r_instrument = top_r['Asset'].values[0]
top_r_figure = round(top_r['R'].values[0], 2)
top_r_pattern = top_r['System Strategy'].values[0]
top_asset = asset_r.idxmax()
top_r_date = top_r['Date'].values[0]
top_r_date_formatted = top_r['Date'].dt.strftime('%d/%m/%Y')
top_r_date = top_r_date_formatted.iloc[0]
top_pa = strategy_r.idxmax()
top_day = day_r.idxmax()
# top_trade_from = positive_r['Trade']
mean_r_by_strategy = df_selection.groupby('System Strategy')['R'].mean().reset_index()
mean_r_by_strategy = mean_r_by_strategy.sort_values(by='R', ascending=False)


# Create a summary metrics here



# --- Charting ---
def plot_line_chart():
    fig = px.line(df_selection, x='Trade ID', y='Rolling R', title='Overall Performance')
    # fig.update_layout(plot_bgcolor='#0d0c3b')
    fig.update_traces(line=dict(color='white'))
    xaxis=dict(showgrid=True, gridcolor='lightgray')
    st.write('This shows the return. When no filter is selected, it plots the overall performance of the entire dataset. Adding filters adjusts the return based on your selection.')
    st.plotly_chart(fig)
    st.markdown('---')

# Strike Rate
wins = df_selection[df_selection['R'] > 0]['R'].count()
losses = df_selection[df_selection['R'] < 0]['R'].count()
total_trades = wins + losses
strike_rate = wins / total_trades
win_percentage = round(strike_rate * 100, 2)
annotation_text = f'{round(win_percentage, 2)}%'


def plot_strike_rate():
    fig = px.pie(
        names=['Wins', 'Losses'],
        values=[wins, losses],
        title='Strike Rate',
        hole=0.7,
        labels={'Wins': 'Wins', 'Losses': 'Losses'}, 
    )
    fig.update_traces(
        marker=dict(colors=['#1717bd', '#2e2e40']),
        text=[f'{wins} Wins', f'{losses} Losses'],  # Display the actual win and loss counts in the chart
        textinfo='none',  # Display both the percentage and label (Wins/Losses)
    )
    fig.add_annotation(
        text=annotation_text,
        x=0.5, y=0.5,  # Position of the annotation in the center of the hole
        showarrow=False,  # Hide the arrow for the annotation
        font=dict(size=32),  # Customize the font size of the annotation
    )
    st.write('The win rate of the overall performance or based on filtering. Strike rates below 50\% must have a Reward to Risk greater than 1.20 to be profitable and account for account fees.')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('---')

def plot_bar_asset():
    df_sorted = df_selection.sort_values(by='R', ascending=False)
    fig = px.bar(df_sorted, x='Asset', y='R', template='seaborn')
    # fig.update_layout()
    st.write('A bar chart to plot the data based on all assets, or filtered ones to get an overall comparison')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('---')

def plot_pie_strategy():
    fig = px.pie(positive_r, values='R', names='System Strategy', hole=0.5)
    fig.update_traces(text=df_selection['System Strategy'], textposition = 'outside')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('---')

def plot_scatter_asset():
    fig = px.scatter(df, 
                     x='Asset', 
                     y='R',
                     title='Asset Scatter Plot'
                     )
    fig.update_layout(
        plot_bgcolor='#10102b',
        xaxis_tickangle=45
    )
    fig.update_traces(marker=dict(color='white'))
    st.plotly_chart(fig)
    st.markdown('---')

def plot_scatter_strategy():
    fig = px.scatter(df, 
                     x='System Strategy', 
                     y='R', 
                     color_continuous_scale='Viridis',
                     title='Strategy Scatter Plot'
                     )
    fig.update_layout(
        plot_bgcolor='#10102b',
        xaxis_tickangle=45
        )
    fig.update_traces(marker=dict(color='white'))
    st.plotly_chart(fig)
    st.markdown('---')


def plot_weekday():
    fig = px.bar(df_selection, 
                x='Day of Week',
                 y='R',
                 title='Performance based on the Day')
    st.write('Performance based on trades that were executed on what day of the week. Helps gain a valuable insight on what types of trades work best on what days. Tracking this helps identify patterns that can be exploited.')
    st.plotly_chart(fig)

def plot_box():
    fig = px.box(df_selection, 
                 x='System Strategy', 
                 y='R', 
                 color='System Strategy', 
                 points='all')
    fig.update_xaxes(title='System Strategy')
    fig.update_yaxes(title='Return')
    st.write('compare the median, quartiles, and outliers across different strategies.')
    st.plotly_chart(fig)
    st.markdown('---')


def plot_heatmap():
    heatmap_data = df.pivot_table(
        index='Asset', 
        columns='System Strategy', 
        values='R', 
        aggfunc='mean') 
    fig = px.imshow(
        heatmap_data,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        color_continuous_scale='Viridis'
    )
    fig.update_xaxes(side="top")  # Move x-axis labels to the top
    fig.update_layout(xaxis_title="System Strategy", yaxis_title="Asset")
    st.write('How different strategies perform across different assets based on average 'R' values. ')
    st.plotly_chart(fig)
    st.markdown('---')

def plot_mean_strategy():
    fig = px.bar(
        mean_r_by_strategy, 
        x='System Strategy',
        y='R'
    )
    fig.update_yaxes(title='Average Return')
    st.plotly_chart(fig)
    st.markdown('---')
    


# --- Page Structures ----
col1, col2 = st.columns(2)
with col1:
    plot_line_chart()
    plot_mean_strategy()
    plot_bar_asset()
    plot_weekday()
    plot_scatter_strategy()
    


with col2:
    plot_strike_rate()
    plot_pie_strategy()
    plot_heatmap()
    plot_box()
    plot_scatter_asset()


# DF explorer
st.write('''
# Explore the data
         Here you can filter out more and explore the dataframe containing all the trades.
'''
         )
df_filter = dataframe_explorer(df, case=False)
st.write(df_filter)