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
st.set_page_config(page_title='JSAX Trade',
                   layout='wide',
                   page_icon='https://jsax.notion.site/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2Fba07c969-ad44-4ac9-b475-1585436607ee%2FUntitled.png?table=block&id=8570f62a-2323-4bbd-ba98-e9043c3fa20b&spaceId=a34bbc1a-8979-401d-ac95-4dc80e288722&width=2000&userId=&cache=v2')
# from streamlit_extras.app_logo import add_logo
from streamlit_extras.dataframe_explorer import dataframe_explorer




# ---- Page description ----
cl1, cl2, cl3 = st.columns(3)
with cl1:
    st.write(' ')
with cl2:
    st.image('https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2F8587d9d9-ebba-474d-bbe3-2220a86e95be%2FUntitled.png?table=block&id=92875c04-e03b-4599-abf2-b810d8ea04df&spaceId=a34bbc1a-8979-401d-ac95-4dc80e288722&width=2000&userId=e094dc45-70bb-460a-8bf7-97e454446eca&cache=v2', width=800)
with cl3: 
    st.write(' ')
# add_logo(r'C:\Users\saleg\Desktop\jupyter\Projects\JSAX_trade_floor\coin_logo.png')
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


# Convert to date
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')


st.write(f"""




""")