import os
import requests
import sqlite3
import pandas as pd

import streamlit as st
import streamlit_extras
from streamlit_lottie import st_lottie
import pygwalker as pyg
import streamlit.components.v1 as components


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

lottie_chart = load_lottie('https://lottie.host/0f3d44f5-42df-4aae-9531-27edb0c1035b/IvakmTFB5G.json')
# Args for lottie - speed=*, 
    # reverse=False, loop=True, quality='low', 
    # render='sug' (canvas), height=*, width=*, key=None


# ---- Page description ----
cl1, cl2, cl3 = st.columns(3)
with cl1:
    st_lottie(lottie_chart, loop=False, speed=0.8)
with cl2:
    st.write(' ')
    st.image('https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2F8587d9d9-ebba-474d-bbe3-2220a86e95be%2FUntitled.png?table=block&id=92875c04-e03b-4599-abf2-b810d8ea04df&spaceId=a34bbc1a-8979-401d-ac95-4dc80e288722&width=2000&userId=e094dc45-70bb-460a-8bf7-97e454446eca&cache=v2', width=800)
with cl3: 
    st.write(' ')
add_logo('https://raw.githubusercontent.com/jsacap/jsax-trade-floor/master/coin_logo.png')
st.title('🔬Strategy Lab')


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


st.write('''
Experiment with different types of variables to determine the most 
effective ones for specific trading scenarios based on collected data.
To visualize the data instantly, drag and drop different columns from 
the left side into the X and Y Axis or the different filters.
         
         ''')
# Generate the HTML using Pygwalker
pyg_html = pyg.walk(df, return_html=True)
 
# Embed the HTML into the Streamlit app
components.html(pyg_html, height=1000, scrolling=True)