# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd

d2checklist_base_url = "https://www.d2checklist.com/clan/3007121"

csv_path = "/Users/rmoctezuma/AppDev/ActivityBot/"
d2_csv_file = "clan-progress-2019-06-02.csv"
clan_positions_file = "clan-positions.csv"

# Read the CSV data from D2 Checklist
d2_data = pd.read_csv(csv_path + d2_csv_file)

# Mark with an 'x' people who have been active in the last 10 days
d2_data['status'] = 'x'
d2_data.loc[d2_data['lastPlayed days ago'] > 10,'status'] = ''

# Take a subset: remove all columns we don't need
d2_data = d2_data[['member','status']]

# Converting their names to lowercase to avoid case issues
d2_data['member_lower'] = d2_data['member'].str.lower()

# Read the Clan positions file, and mark officers, admins and sherpas
clan_positions = pd.read_csv(csv_path + clan_positions_file)
d2_data = d2_data.merge(clan_positions, how = 'left', on = 'member')
d2_data.position = d2_data.position.fillna(999)

# Sort it
d2_data = d2_data.sort_values(['position','status','member_lower'],ascending=[True,False,True])

# Take a subset: leave only the columns that we need to upload
d2_data = d2_data[['member','status']]

# Write the CSV file
d2_data.to_csv(csv_path + 'processed.csv')

