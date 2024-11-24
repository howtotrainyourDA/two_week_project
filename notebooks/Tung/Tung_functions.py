import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



"""
input: df
output: df

function to extract only the latest session per client based on visit_id

"""

def valid_session(df: pd.DataFrame) -> pd.DataFrame:
    df['date_time'] = pd.to_datetime(df['date_time'])
    
    most_recent_sessions = df.loc[df.groupby('client_id')['date_time'].idxmax()]
    
    df_recent = df[df['visit_id'].isin(most_recent_sessions['visit_id'])]
    
    df_recent = df_recent.sort_values(by=['client_id', 'visitor_id', 'date_time'])

    return df_recent




step_mapping = {
        'start': 0,
        'step_1': 1,
        'step_2': 2,
        'step_3': 3,
        'confirm': 4
    }
"""
input: df
output: df

function to map "process_step" for easier sorting of process steps
"""

def step_map(df):
    df["process_step_num"] = df["process_step"].map(step_mapping)
    df = df.sort_values(by=["client_id", "process_step_num"], ascending = True)

    return df




"""
input: df
output: df

function for total average step time and start-to-confirm
"""

def calculate_avg_time(df):
    df['date_time'] = pd.to_datetime(df['date_time'])

    df.sort_values(by=['visit_id', 'date_time'], inplace=True)

    df['time_diff'] = df.groupby('visit_id')['date_time'].diff()

    # Filter out rows where time_diff is NaT (first row of each visit_id)
    df = df.dropna(subset=['time_diff'])

    average_time_per_step = df.groupby('process_step')['time_diff'].mean()

    #convert date_time to seconds
    average_time_per_step = average_time_per_step.dt.total_seconds()

    start_confirm_df = df[df['process_step'].isin(['start', 'confirm'])]

    start_confirm_df.loc[:, 'time_diff'] = start_confirm_df.groupby('visit_id')['date_time'].diff()

    #keep only "confirm" rows
    start_to_confirm_time = start_confirm_df[start_confirm_df['process_step'] == 'confirm']

    avg_time_start_to_confirm = start_to_confirm_time['time_diff'].mean().total_seconds()  / 60


    print("Average time per process step (in seconds):")
    print(average_time_per_step.round(2))

    print(f"\nAverage time from 'start' to 'confirm': {avg_time_start_to_confirm} min / {avg_time_start_to_confirm * 60} seconds")

