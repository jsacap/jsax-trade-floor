import os
import sqlite3
import requests
import datetime as dt
import pandas as pd
import streamlit as st

st.set_page_config(layout='wide')
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


# ---- Page description ----
cl1, cl2, cl3 = st.columns(3)
with cl1:
    st.write(' ')
with cl2:
    st.image('https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2F8587d9d9-ebba-474d-bbe3-2220a86e95be%2FUntitled.png?table=block&id=92875c04-e03b-4599-abf2-b810d8ea04df&spaceId=a34bbc1a-8979-401d-ac95-4dc80e288722&width=2000&userId=e094dc45-70bb-460a-8bf7-97e454446eca&cache=v2', width=800)

with cl3: 
    st.write(' ')

# from streamlit_extras.app_logo import add_logo

# add_logo(r'C:\Users\saleg\Desktop\jupyter\Projects\JSAX_trade_floor\coin_logo.png')
st.title('Trade Management')

st.write("""In this section, you can edit, delete, and close trades. To edit a trade, simply double-click any of the cells, make your changes, and hit Enter. Then, click "Save Changes" to write your edits back to the database.

To delete a trade/row, click the checkbox on the left side of the first column, press DEL on your keyboard, and save your changes.

To close a trade, double-click the "Result" cell of the trade you wish to close, enter the resulting pips, and press Enter. Save the changes and we'll take care of the rest by calculating the changes made and updating the database.
""")




# Functions for calculations
def date_format():
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
    df['Day of Week'] = df['Date'].dt.day_name()
    return df


def calculate_r(df):
    df['R'] = (df['Result'] / df['Stop Loss']).round(2)
    df['Rolling R'] = df['R'].cumsum()
    return df

def update_fields(row_index, editable_df):
    row = editable_df.iloc[row_index]
    # Update Trade ID
    df['Trade ID'] = df.index + 1

    # Update calculations for the edited row
    r = round(row['Result'] / row['Stop Loss'],
              2) if row['Stop Loss'] != 0 else 0
    if row_index == 0:
        rolling_r = r
    else:
        rolling_r = editable_df['Rolling R'].iloc[row_index - 1] + r
    editable_df.at[row_index, 'R'] = r
    editable_df.at[row_index, 'Rolling R'] = rolling_r
    return editable_df

# Editable DF
editable_df = st.data_editor(df, num_rows='dynamic')

if st.button('Save Changes'):
    df = editable_df
    calculate_r(df)
    for row_index in range(len(df)):
        df = update_fields(row_index, df)

    conn = sqlite3.connect(db_file)
    df.to_sql('trades', conn, if_exists='replace', index=False)
    conn.close()
    st.success('Changes saved successfully')