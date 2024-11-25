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


#this stores the avg time in a seperate column to do the hypothesis testing. 


def calculate_avg_time(df):
    # Step 1: Convert 'date_time' to datetime
    df['date_time'] = pd.to_datetime(df['date_time'])

    # Step 2: Sort values by 'visit_id' and 'date_time'
    df.sort_values(by=['visit_id', 'date_time'], inplace=True)

    # Step 3: Calculate the time differences (in seconds) between each row's 'date_time'
    df['time_diff'] = df.groupby('visit_id')['date_time'].diff().dt.total_seconds()

    # Step 4: Create new columns for each step-to-step time difference
    # From 'start' to 'step_1', 'step_1' to 'step_2', etc.
    df['start_to_step_1_time'] = df.groupby('visit_id')['time_diff'].shift(-1)
    df['step_1_to_step_2_time'] = df.groupby('visit_id')['time_diff'].shift(-2)
    df['step_2_to_step_3_time'] = df.groupby('visit_id')['time_diff'].shift(-3)
    df['step_3_to_confirm_time'] = df.groupby('visit_id')['time_diff'].shift(-4)

    # Step 5: Calculate the total time from 'start' to 'confirm' for each client
    # We will use the 'time_diff' for the difference between 'start' and 'confirm'
    start_confirm_df = df[df['process_step'].isin(['start', 'confirm'])]
    start_confirm_df['time_diff'] = start_confirm_df.groupby('visit_id')['date_time'].diff().dt.total_seconds()
    
    # Keep only 'confirm' rows (these represent the end of the process)
    start_to_confirm_time = start_confirm_df[start_confirm_df['process_step'] == 'confirm']
    df['total_start_to_confirm_time'] = start_to_confirm_time.groupby('visit_id')['time_diff'].transform('sum')

    # Step 6: Return the dataframe with time differences per step for each client
    return df