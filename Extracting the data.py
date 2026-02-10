# -*- coding: utf-8 -*-
"""
This file extracts the time trial data from the excel sheet on google drive

An example on how to get the sheet id
    If your sheet url is: https://docs.google.com/spreadsheets/d/1xRLXJtq75ceznTB74k36_ZTj9DBXYiGu7WVaXQWltnY/edit?resourcekey=&gid=907516662#gid=907516662
    The sheet id is between d/ and /edit --> 1xRLXJtq75ceznTB74k36_ZTj9DBXYiGu7WVaXQWltnY
    And the GID is the last number --> 907516662
    The url requires: https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/export?format=csv&gid=<GID>
    Thus, the <spreadsheet_ID> has to be replaced with your specific sheet id and <GID> with the gid number
    Final: https://docs.google.com/spreadsheets/d/1xRLXJtq75ceznTB74k36_ZTj9DBXYiGu7WVaXQWltnY/export?format=csv&gid=907516662
"""

# Import the modules used
import pandas as pd



# First, find the file and create a dataframe
Sheet_id = "1xRLXJtq75ceznTB74k36_ZTj9DBXYiGu7WVaXQWltnY"  # This should be replaced with the relavant sheet id each year
GID_number = "907516662"   # This should also be replaced each year
url_first = "https://docs.google.com/spreadsheets/d/"
url_last = "/export?format=csv&gid="

url = url_first + Sheet_id + url_last + GID_number
df = pd.read_csv(url)

# Check if transformation has worked
print(df.info())
print(df.describe())



# Adding example names
names = ["Joa", "Josh", "Stefan", "Conrad", "Barry", "Tayla"]
surnames = ["Theron", "Glyn-Cuthbert", "Erlank", "Kriel", "Muller", "Isaac"]
times = ["00:30:00", "00:48:00", "00:51:00", "00:53:00", "00:42:00", "01:02:00"]
distance = ["5 km", "10 km", "10 km", "10 km", "5 km", "10 km"]
df_new = pd.DataFrame([
    {
        "Timestamp": "02/22/2026 10:10:10",
        "Name": f"{names[i]}",
        "Surname": f"{surnames[i]}",
        "Did you do short or long dice?": f"{distance[i]}",
        "Please submit your time": pd.to_timedelta(f"{times[i]}"),
    }
    for i in range(6)
])

# append to original DataFrame
df = pd.concat([df, df_new], ignore_index=True)






# Now, lets clean and transform the data
## The timestamp has the date and the time. Time is unimportant and we want to separate the date.
df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%m/%d/%Y %H:%M:%S")

df["dd"] = df["Timestamp"].dt.day
df["mm"] = df["Timestamp"].dt.month
df["yy"] = df["Timestamp"].dt.year

df = df.drop(columns="Timestamp")
df["race_date"] = df["dd"].astype(str).str.zfill(2) + "/" + df["mm"].astype(str).str.zfill(2)  # Create a new column to identify each race

## Next, we want to convert the entered time to a datetime
df["Please submit your time"] = pd.to_timedelta(df["Please submit your time"])

## Now, we sort and create separate dices for 5km and 10km
df = df.sort_values(by = ["dd", "Please submit your time"])

df_5km = df[df["Did you do short or long dice?"] == "5 km"]
df_10km = df[df["Did you do short or long dice?"] == "10 km"]

## The final step is pivoting our dataframe so that each race is a column and each person a row
df_5km_final = (df_5km.pivot_table(
    index = ["Name", "Surname"], 
    columns = "race_date",
    values = "Please submit your time",
    aggfunc = "first"
    ).sort_index(axis=1)
)

df_10km_final = (df_10km.pivot_table(
    index = ["Name", "Surname"], 
    columns = "race_date",
    values = "Please submit your time",
    aggfunc = "first"
    ).sort_index(axis=1)
)



# Now, create the streamlit app






