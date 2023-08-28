import os
import sqlite3
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import requests

# Layout

st.set_page_config(page_title='JSAX Trade', page_icon='https://jsax.notion.site/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2Fba07c969-ad44-4ac9-b475-1585436607ee%2FUntitled.png?table=block&id=8570f62a-2323-4bbd-ba98-e9043c3fa20b&spaceId=a34bbc1a-8979-401d-ac95-4dc80e288722&width=2000&userId=&cache=v2', layout='centered')
st.image('https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2F8587d9d9-ebba-474d-bbe3-2220a86e95be%2FUntitled.png?table=block&id=92875c04-e03b-4599-abf2-b810d8ea04df&spaceId=a34bbc1a-8979-401d-ac95-4dc80e288722&width=2000&userId=e094dc45-70bb-460a-8bf7-97e454446eca&cache=v2', width=600)
st.header('🏦JSAX TRADE')
# from streamlit_extras.app_logo import add_logo
# add_logo(r'C:\Users\saleg\Desktop\jupyter\Projects\JSAX_trade_floor\coin_logo.png')


st.markdown("---")


# Hide ST HTML
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


    if 'index' in df.columns:
        df = df.drop('index', axis=1)  # Drop the existing index column
        df.reset_index(drop=True, inplace=True)  # Reset the row indices
        df['Trade ID'] = df.index + 1  # Create a new Trade ID column
        # Calculate Rolling R values only for rows with None values
        rolling_r_mask = df['Rolling R'].isnull()
        df.loc[rolling_r_mask, 'Rolling R'] = df.loc[rolling_r_mask, 'R'].cumsum()

        # Save the updated DataFrame back to the database
        conn = sqlite3.connect(db_file)
        df.to_sql('trades', conn, index=False, if_exists='replace')  # Replace the existing table with the updated DataFrame
        conn.close()
    
    return df

df = load_data()



# Prep Data for charts
asset_return = df.groupby('Asset')['R'].sum(
).sort_values(ascending=False).round(2)

if not asset_return.empty:
    top_asset = asset_return.index[0]
else:
    top_asset = None  # Or any default value you prefer

top_asset_r = asset_return.iloc[0]
net_r = float(round(df['R'].sum(), 2))


# Charting
def rolling_r_update():
    df['Rolling R'] = df['Rolling R'].fillna(df['R'].iloc[0])
    df['Rolling R'] = df['R'].cumsum()
    df.to_csv('trades.csv', index=False)

def plot_line_chart():
    st.subheader('R Curve')
    plt.style.use('fivethirtyeight')
    fig_r_curve, ax_r_curve = plt.subplots(figsize=(10, 6))
    sns.lineplot(x='Trade ID', y='Rolling R', data=df,
                 color='navy', ax=ax_r_curve)
    ax_r_curve.set_title('R Multiple')
    ax_r_curve.set_xlabel('Trade ID')
    ax_r_curve.set_ylabel('Rolling R')
    plt.tight_layout()
    st.pyplot(fig_r_curve)


def plot_asset_return_chart():
    # Asset Return
    st.subheader('Asset Based Returns')
    fig_asset_return, ax_asset_return = plt.subplots(figsize=(10, 6))
    ax_asset_return.bar(asset_return.index, asset_return.values, color='navy')
    ax_asset_return.set_xlabel('Asset')
    ax_asset_return.set_ylabel('R')
    ax_asset_return.set_xticklabels(
        asset_return.index, rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig_asset_return)


# Prep data for the strike rate
wins = df[df['R'] > 0]['R'].count()
losses = df[df['R'] < 0]['R'].count()
total_trades = wins + losses
strike_rate = wins / total_trades
round(strike_rate * 100, 2)


def plot_strike_rate():
    # Plotting the donut strike rate
    st.subheader('Win to Loss Ratio')
    # Create labels and data for the chart
    labels = ['Wins', 'Losses']
    sizes = [wins, losses]

    # Set colors for the chart
    colors = ['#001F3F', '#CCCCCC']

    # Create a donut chart
    fig, ax = plt.subplots(figsize=(10, 6))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct='', startangle=90, wedgeprops={'edgecolor': 'white'})

    # Draw a white circle at the center to create the donut effect
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig.gca().add_artist(centre_circle)

    # Calculate and display win percentage in the center
    win_percentage = round((wins / total_trades) * 100, 2)
    ax.text(0, 0, f'{win_percentage}%', fontsize=30,
            color='black', va='center', ha='center')

    ax.axis('equal')
    ax.set_title('Strike Rate')

    st.pyplot(plt)

# Date formatting for delta stat
df2 = df
df2['Date'] = pd.to_datetime(df2['Date'], format='%d/%m/%Y')
current_month = pd.Timestamp.today().replace(day=1)
previous_month_close = current_month - pd.DateOffset(days=1)
previous_month_df = df2[(df2['Date'] >= previous_month_close.replace(day=1)) & (df2['Date'] <= previous_month_close)]
rolling_r_previous_month = previous_month_df.iloc[-1]['Rolling R']
current_rolling_r = df2.iloc[-1]['Rolling R']
change_this_month = round(current_rolling_r - rolling_r_previous_month, 2)

def main():
    rolling_r_update()

    col1, col2, col3 = st.columns(3)
    col1.metric('Top Perming Asset', top_asset)
    col2.metric('Return on Top Asset (R)', top_asset_r)
    col3.metric('Net R', net_r, delta=f'{change_this_month} R this month')

    st.markdown("---")
    plot_line_chart()
    leftcol, rightcol = st.columns(2)


    with leftcol:
        plot_asset_return_chart()

    with rightcol:
        plot_strike_rate()
    st.write(df)
    

if __name__ == "__main__":
    main()