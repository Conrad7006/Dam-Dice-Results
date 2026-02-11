# -*- coding: utf-8 -*-
"""
This file extracts the time trial data from the excel sheet on google drive
Just note that the excel sheet must be set to "anyone with the link" under the share option

An example on how to get the sheet id
    If your sheet url is: https://docs.google.com/spreadsheets/d/1ZwtX-6lr_AwZnP1KmoIG8AfK3iQYioJuVMBR2Dqac6s/edit?resourcekey=&gid=199477171#gid=199477171
    The sheet id is between d/ and /edit --> 1ZwtX-6lr_AwZnP1KmoIG8AfK3iQYioJuVMBR2Dqac6s
    And the GID is the last number --> 199477171
    The url requires: https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/export?format=csv&gid=<GID>
    Thus, the <spreadsheet_ID> has to be replaced with your specific sheet id and <GID> with the gid number
    Final: https://docs.google.com/spreadsheets/d/1xRLXJtq75ceznTB74k36_ZTj9DBXYiGu7WVaXQWltnY/export?format=csv&gid=907516662
"""

# Import the modules used
import pandas as pd
import streamlit as st



# First, find the file and create a dataframe
Sheet_id = "1ZwtX-6lr_AwZnP1KmoIG8AfK3iQYioJuVMBR2Dqac6s"  # This should be replaced with the relavant sheet id each year
GID_number = "199477171"   # This should also be replaced each year
url_first = "https://docs.google.com/spreadsheets/d/"
url_last = "/export?format=csv&gid="

url = url_first + Sheet_id + url_last + GID_number
df = pd.read_csv(url)



# Adding example names (only for testing purposes)
#names = ["Joa", "Josh", "Stefan", "Conrad", "Barry", "Tayla"]
#surnames = ["Theron", "Glyn-Cuthbert", "Erlank", "Kriel", "Muller", "Isaac"]
#times = ["00:30:00", "00:48:00", "00:51:00", "00:53:00", "00:42:00", "01:02:00"]
#distance = ["5 km", "10 km", "10 km", "10 km", "5 km", "10 km"]
#df_new = pd.DataFrame([
#    {
#        "Did you do doubles?": "No",
#        "Timestamp": "02/22/2026 10:10:10",
#        "Name": f"{names[i]}",
#        "Surname": f"{surnames[i]}",
#        "Did you do short or long dice?": f"{distance[i]}",
#        "Please submit your time": pd.to_timedelta(f"{times[i]}"),
#    }
#    for i in range(6)
#])
# append to original DataFrame
#df = pd.concat([df, df_new], ignore_index=True)



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

## Then, we replace the doubles answer with a 1 or 0
def doubles_check(Answer):
    if Answer == "Yes":
        return 1
    elif Answer == "No":
        return 0

df["Did you do doubles?"] = df["Did you do doubles?"].apply(doubles_check)

## Now, we sort and create separate dices for 5km and 10km
df = df.sort_values(by = ["race_date", "Please submit your time"])

df_5km = df[df["Did you do short or long dice?"] == "5 km"].copy()
df_10km = df[df["Did you do short or long dice?"] == "10 km"].copy()

## Now compute a rank for each paddler based on the day and double the rank for doubles
df_5km["Rank"] = df_5km.groupby("race_date")["Please submit your time"].rank(method="dense")    # "dense" causes doubles boats to be considered together
df_10km["Rank"] = df_10km.groupby("race_date")["Please submit your time"].rank(method="dense")  

df_5km["Bobaas"] = df_5km["Rank"] + df_5km["Rank"] * df_5km["Did you do doubles?"]
df_10km["Bobaas"] = df_10km["Rank"] + df_10km["Rank"] * df_10km["Did you do doubles?"]

## Pivot the dataframe so that each race is a column and each person a row
df_5km_yster = (df_5km.pivot_table(
    index = ["Name", "Surname"], 
    columns = "race_date",
    values = "Please submit your time",
    aggfunc = "first"
    ).sort_index(axis=1)
)

df_10km_yster = (df_10km.pivot_table(
    index = ["Name", "Surname"], 
    columns = "race_date",
    values = "Please submit your time",
    aggfunc = "first"
    ).sort_index(axis=1)
)

## Create a number of races column for the yster competition
df_5km_yster["# Races"] = df_5km_yster.notna().sum(axis=1)
df_10km_yster["# Races"] = df_10km_yster.notna().sum(axis=1)

## Now that calculations are done, create a display copy for streamlit (timedelta is not nice)
df_5km_yster_display = df_5km_yster.applymap(
    lambda x: str(x).replace("0 days ", "") if pd.notna(x) else ""
)

df_10km_yster_display = df_10km_yster.applymap(
    lambda x: str(x).replace("0 days ", "") if pd.notna(x) else ""
)

## Pivot the dataframe so that each race is a column and each person is a row with bobaas points as the indeces
df_5km_bobaas = (df_5km.pivot_table(
    index = ["Name", "Surname"], 
    columns = "race_date",
    values = "Bobaas",
    aggfunc = "first"
    ).sort_index(axis=1)
)

df_10km_bobaas = (df_10km.pivot_table(
    index = ["Name", "Surname"], 
    columns = "race_date",
    values = "Bobaas",
    aggfunc = "first"
    ).sort_index(axis=1)
)

df_5km_rank = (df_5km.pivot_table(
    index = ["Name", "Surname"], 
    columns = "race_date",
    values = "Rank",
    aggfunc = "first"
    ).sort_index(axis=1)
)

df_10km_rank = (df_10km.pivot_table(
    index = ["Name", "Surname"], 
    columns = "race_date",
    values = "Rank",
    aggfunc = "first"
    ).sort_index(axis=1)
)

## Now create the Bobaas ranking column
df_10km_bobaas["Total"] = 225 - (15 - df_10km_bobaas).clip(lower=0).sum(axis=1)  # Clip(lower=0) replaces negative values with 0
df_5km_bobaas["Total"] = 225 - (15 - df_5km_bobaas).clip(lower=0).sum(axis=1)

# %%

# Now, create the streamlit app
st.set_page_config(page_title="Maties Canoeing Dam Dice Results", layout="wide")

## Create the sidebar for navigation between the different pages
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Go to:",
    ["Main", "Yster", "Bobaas"],
)

## Create the page for each sidebar section
### First, the main page that includes the rankings and some info on time trial
if menu == "Main":
    st.title("Maties Canoeing Dam Dice Results")

    # Show the two rank dataframes
    st.write("The results of our 10 km dam dices")
    st.dataframe(df_10km_rank)
    
    st.write("\nThe results of our 5 km dam dices")
    st.dataframe(df_5km_rank)

### Next, the page that contains information on the Yster competition
elif menu == "Yster":
    st.title("The Yster Competition")
    
    # Show the two yster dataframes
    st.write("The results of our 10 km dam dices")
    st.dataframe(df_10km_yster_display)
    
    st.write("\nThe results of our 5 km dam dices")
    st.dataframe(df_5km_yster_display)
    
### Finally, the page that contains information on the Bobaas competition
elif menu == "Bobaas":
    st.title("The Bobaas Competition")
    
    # Show the two bobaas dataframes
    st.write("The results of our 10 km dam dices")
    st.dataframe(df_10km_bobaas)
    
    st.write("\nThe results of our 5 km dam dices")
    st.dataframe(df_5km_bobaas)
    
    
    
    
    
    
    
    

