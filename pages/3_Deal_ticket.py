import pandas as pd
import requests
import datetime as dt
import streamlit as st
import os
import seaborn as sns
import matplotlib.pyplot as plt
import sqlite3
# Layout

st.image('https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2F8587d9d9-ebba-474d-bbe3-2220a86e95be%2FUntitled.png?table=block&id=92875c04-e03b-4599-abf2-b810d8ea04df&spaceId=a34bbc1a-8979-401d-ac95-4dc80e288722&width=2000&userId=e094dc45-70bb-460a-8bf7-97e454446eca&cache=v2', width=600)
# from streamlit_extras.app_logo import add_logo
# add_logo(r'C:\Users\saleg\Desktop\jupyter\Projects\JSAX_trade_floor\coin_logo.png')


# Hide ST HTML

hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

st.header('Deal Ticket')

# GitHub raw content URLs
base_url = "https://raw.githubusercontent.com/jsacap/jsax-trade-floor/master/"
csv_url = base_url + "trades.csv"
db_url = base_url + "trades.db"

def load_data():
    db_response = requests.get(db_url)
    with open('trades.db', 'wb') as db_file:
        db_file.write(db_response.content)
    conn = sqlite3.connect('trades.db')
    query = "SELECT * FROM trades"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

df = load_data()


st.write(
    'Add new trades here. Fill in the deal ticket below to add the trade to the Trade Journal.')

# Use columns for layout
col1, col2 = st.columns(2)

# Column 1
with col1:
    asset = st.text_input("Asset")
    date = st.date_input("Date", dt.datetime.now().date())
    date_str = date.strftime("%d/%m/%Y")  # Format the date
    time = st.time_input("Time", value=dt.datetime.now(
    ).time().replace(second=0, microsecond=0))
    stop_loss = st.number_input("Stop Loss")
    trade_type = st.selectbox(
        "Trade Type", ['Trend-Continuation', 'Counter-Trend', 'Advanced-Pattern'])
    system_strategy = st.text_input("System Strategy")

# Column 2
with col2:
    timeframe = st.selectbox('Timeframe', [60, 15, 5, 240])
    htf_trend = st.selectbox("In-line with HTF/LTF Trend?", ['Yes', 'No'])
    trade_from = st.selectbox('Trade From...', [
        'HTF KZ1', 'HTF KZ3', 'LTF KZ1', 'LTF KZ3', 'TTF KZ1', 'TTF KZ3', 'iS KZ1', 'iS KZ3', 'VPP', 'Pi', 'TL'])
    direction = st.selectbox("Direction", ['Long', 'Short'])
    result = st.number_input("Result")

# Apply custom CSS styling
st.markdown("""
<style>
.stButton > button {
    background-color: navy;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 8px 16px;
}
</style>
""", unsafe_allow_html=True)

# Submit button within the form context manager
with st.form(key='new_trade_form'):
    if st.form_submit_button(label="Submit"):
        # Auto Day
        day_of_week = date.strftime('%A')
        
        # Auto R
        if result != 0:
            r = round(result / stop_loss, 2)
        else:
            r = 0

        if not df.empty:
            previous_rolling_r = df['Rolling R'].iloc[-1]
            rolling_r = previous_rolling_r + r
        else:
            rolling_r = r

        # Ensure correct date format to db
        date_str = date.strftime("%d/%m/%Y")

        # Create a new row dictionary
        new_row = {
            'Asset': asset,
            'Date': date_str,
            'Time': time,
            'Stop Loss': stop_loss,
            'Trade Type': trade_type,
            'System Strategy': system_strategy,
            'Timeframe': timeframe,
            'HTF Trend': htf_trend,
            'Trade From': trade_from,
            'Day of Week': day_of_week,
            'Direction': direction,
            'Result': result,
            'R': r,
            'Rolling R': rolling_r
        }

        

        # Write to db
        # df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        new_row_df = pd.DataFrame([new_row])
        new_row['Rolling R'] = rolling_r
        # Reset index for the new_row_df
        new_row_df = new_row_df.reset_index(drop=True)
        # Reset index for the entire df
        df_reset = df.reset_index(drop=True)
        conn = sqlite3.connect(db_file)
        new_row_df.to_sql('trades', conn, if_exists='append', index=False)
        query_post_trade = f'SELECT * FROM trades ORDER BY rowid DESC LIMIT 5'
        db_tail = pd.read_sql(query_post_trade, conn)
        conn.close()
        st.success('Trade successfully saved to database')
        st.write(f'You traded the {asset}, and used the {system_strategy} for your entry on the {timeframe} timeframe. The entry was from the {trade_from}, and was a {trade_type} trade.')
        st.write(db_tail)
