# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime

# load data
@st.cache_data
def load_data():
    df_agg = pd.read_csv('Aggregated_Metrics_By_Video.csv').iloc[1:,:]
    # rename columns to get rid of weird ascii chars
    df_agg.columns = ['Video','Video title','Video publish time','Comments added','Shares','Dislikes','Likes',
                      'Subscribers lost','Subscribers gained','RPM(USD)','CPM(USD)','Average % viewed','Average view duration',
                      'Views','Watch time (hours)','Subscribers','Your estimated revenue (USD)','Impressions','Impressions ctr(%)']
    # convert pusblish time to datetime
    df_agg['Video publish time'] = pd.to_datetime(df_agg['Video publish time'], format='%b %d, %Y')
    df_agg['Average view duration'] = df_agg['Average view duration'].apply(lambda x: datetime.strptime(x,'%H:%M:%S'))
    df_agg['Avg_duration_sec'] = df_agg['Average view duration'].apply(lambda x: x.second + x.minute*60 + x.hour*3600)
    df_agg['Engagement_ratio'] =  (df_agg['Comments added'] + df_agg['Shares'] +df_agg['Dislikes'] + df_agg['Likes']) /df_agg.Views
    df_agg['Views / sub gained'] = df_agg['Views'] / df_agg['Subscribers gained']
    df_agg.sort_values('Video publish time', ascending = False, inplace = True)    
    df_agg_sub = pd.read_csv('Aggregated_Metrics_By_Country_And_Subscriber_Status.csv')
    df_comments = pd.read_csv('Aggregated_Metrics_By_Video.csv')
    df_time = pd.read_csv('Video_Performance_Over_Time.csv')
    # Preprocess the 'Date' column to replace 'Sept' with 'Sep'
    df_time['Date'] = df_time['Date'].str.replace('Sept', 'Sep')
    df_time['Date'] = pd.to_datetime(df_time['Date'], format='%d %b %Y')
    return df_agg, df_agg_sub, df_comments, df_time

df_agg, df_agg_sub, df_comments, df_time = load_data()
# engineer data
df_agg_diff = df_agg.copy()
metric_date_12mo = df_agg_diff['Video publish time'].max() - pd.DateOffset(months =12)
median_agg = df_agg_diff[df_agg_diff['Video publish time'] >= metric_date_12mo].median()


# build dashboard
add_sidebar = st.sidebar.selectbox('Aggregate or Individual Video', ('Agregate Metrics', 'Individual Video Analysis'))
