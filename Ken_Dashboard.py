# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime

AGG = 'Aggregate Metrics'
IND = 'Individual Video Analysis'

def style_negative(v, props=''):
    try:
        return props if v < 0 else None
    except:
        pass # if not a numeric
    
def style_positve(v, props=''):
    try:
        return props if v > 0 else None
    except:
        pass # if not a numeric

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
median_agg = df_agg_diff[df_agg_diff['Video publish time'] >= metric_date_12mo].median(numeric_only=True)
numeric_cols = np.array((df_agg_diff.dtypes == 'float64') | (df_agg_diff.dtypes == 'int64'))
df_agg_diff.iloc[:,numeric_cols] = (df_agg_diff.iloc[:,numeric_cols] - median_agg).div(median_agg)
 

# build dashboard
add_sidebar = st.sidebar.selectbox('Aggregate or Individual Video', (AGG, IND))

## total picture
if add_sidebar == AGG:
    df_agg_metrics = df_agg[['Video publish time','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)','Average % viewed',
                             'Avg_duration_sec', 'Engagement_ratio','Views / sub gained']]
    metric_date_6mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months =6)
    metric_date_12mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months =12)
    metric_medians6mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metric_date_6mo].median(numeric_only=True)
    metric_medians12mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metric_date_12mo].median(numeric_only=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]
    
    count = 0
    for i in metric_medians6mo.index:
        with columns[count]:
            delta = (metric_medians6mo[i] - metric_medians12mo[i])/metric_medians12mo[i]
            st.metric(label= i, value = round(metric_medians6mo[i], 1), delta = "{:.2%}".format(delta))
            count += 1
            if count >= 5:
                count = 0
                
    df_agg_diff['Publish_date'] = df_agg_diff['Video publish time'].apply(lambda x: x.date())
    df_agg_diff_final = df_agg_diff.loc[:,['Video title','Publish_date','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)','Average % viewed',
                             'Avg_duration_sec', 'Engagement_ratio','Views / sub gained']]
    
    df_agg_numeric_lst = df_agg_diff_final.median(numeric_only=True).index.tolist()
    df_to_pct = {}
    for i in df_agg_numeric_lst:
        df_to_pct[i] = '{:.1%}'.format
    
    st.dataframe(df_agg_diff_final.style.applymap(style_negative, props= 'color:red').applymap(style_positve, props= 'color:green').format(df_to_pct))
    
if add_sidebar == IND:
    st.write('Ind')