#!/usr/bin/env python
# coding: utf-8

# # Data Exploration Performance

# In[3]:


from myfunc import * # also imports numpy as np, pandas as pd, copy, datetime and json
import random
import sqlalchemy as sa
from pymongo import MongoClient
import requests
import geopandas as gpd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.figure_factory as ff
from matplotlib_venn import venn2, venn2_circles
from plotly.offline import init_notebook_mode
init_notebook_mode() # To show plotly plots when notebook is exported to html


# In[1]:


get_ipython().system('brew services start mongodb-community@5.0')


# In[4]:


client = MongoClient()
client = MongoClient('mongodb://localhost:27017/')
mydb = client['swimmerData']
mycol = mydb.get_collection('performance')
print('Databases:',client.list_database_names())


# In[44]:


conf = connectDatabase('configPostgresSQL.json')
conn_str = 'postgresql://%s:%s@localhost:5432/%s'%(conf["user"], conf["passw"],conf["database"])
engine = sa.create_engine(conn_str)
inspector = sa.inspect(engine)


# ## Questions
# 
# In this chapter the performances of every athlete will be explored.
# 
# As discussed in the webscrapping chapter only the data for currently active athletes was scrapped. The data is stored in a mongoDB database and has following structure.
# 
# <br>
# Example for Dict Structure:
# 
# {<br>
#     &nbsp;&nbsp;&nbsp;&nbsp;'id':'123456',<br>
#     &nbsp;&nbsp;&nbsp;&nbsp;'season':'2020',<br>
#     &nbsp;&nbsp;&nbsp;&nbsp;'100m Freestyle':[{<br>
#         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'Date': 'some date',<br>
#         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'Place': 'somewhere',<br>
#         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'Course': 'pool distance',<br>
#         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'Time': 'some value',<br>
#         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'Points': 'some value'<br>
#     &nbsp;&nbsp;&nbsp;&nbsp;}]<br>
# }
# 
# Based on this following questions are examind:
# * What kind of events where participated in?
# * Which is the most favourite event for athletes?
# * When did season 2020 and 2021 start and end?
# * What is the relation between points and time?
# * Where do the competitions take place?
# 
# ## Pipelines and Queries
# 
# To access the mongoDB database the find or the aggregate functions from pymongo are used on the collection. While building those pipelines / queries it occured that for some time-values the letter M is attached. Additionnaly some Dates have the letter T at the end. Those letters will be removed to get pipelines and queries work with numerical data operations.
# 
# This could have prevented with checking the data before loading it into the mongoDB, because the pipelines had to be designed more complex. However, it provided an awesome learning opportunity. The results are in My Functions.
# 
# ![](pictures/Beispiel_M_inTime.png)<br>
# (Source: [swimrankings.net Athlete: Szebasztian Szabo](https://www.swimrankings.net/index.php?page=athleteDetail&athleteId=5364206&result=2021))
# 

# In[14]:


pipeline = [
    {'$unwind':'$100m Freestyle'},
    {'$match':{'100m Freestyle.Course':'50m','id':'5364206'}},
    {'$project':{'100m Freestyle.Time':1,'_id':0}}
]

list(mycol.aggregate(pipeline))


# ## Overview on Events
# 
# First a pandas dataframe is generated that holds the count of events per season.
# 
# From this output a set of events is generated. The print() function is used to prevent a long output with one line per event.</br>
# 
# Not fully understood is the difference between events with and without the addition *Lap*.
# The picture shows the 2020 data for Caleb Dressel. Therein 50m Freestyle and 50m Freestyle Lab events are shown. The only difference that can be found is that *Lab* does not state points. Therefore for the planned Montecarlo Simulation the times in *Lab* events shall also be considered.
# 
# ![title](pictures/Dressel_2020_Freistil.png)<br>(Source: [swimrankings.net Athlete: Caeleb Dressel](https://www.swimrankings.net/index.php?page=athleteDetail&athleteId=4772537&result=2020))

# In[6]:


df = pd.concat([create_dataframe_for_season(2020,mycol),create_dataframe_for_season(2021,mycol)]).groupby(['event','season']).sum().reset_index()
df.head()


# In[7]:


events = list(set(df['event']))
print(events)


# ## Most favourite Events
# 
# Following output shows that the 100m Freestyle events are the most common for the athletes. Closely followed by 50m and 200m Freestyle.</br>
# 
# It is to highlight that this value is the sum of keys for eventtypes. Within each event could be several more entries for each participation of an athlete.</br>
# From the output it is seen that 100m Freestyle was the most favored event in 2020 and 2021. Followed by 50m and 200m Freestyle.
# 
# Lower values where cut of to keep the plot accessable.

# In[35]:


df.sort_values(['times','season'],ascending=False).head(8)


# In[22]:


df['season'] = df['season'].astype(str) # to get grouped bars in plot


# In[40]:


fig = px.bar(df.sort_values(['times','season'],ascending=False).head(8),y='event',x='times',color='season',title='Number of athletes who participated in a specific event at least once',barmode='group')
fig.update_layout(
    xaxis_title="Number of athletes",
    yaxis_title="Event",
    plot_bgcolor='#ededed',
    yaxis={'categoryorder':'total ascending'}
)
fig.show()


# ## Season durations
# 
# When requesting the min and max dates for each season an interesting overlap is seen.
# 
# Season 2020 starts in the second half and ends in December 2020. Despite the fact that season 2021 already started in the second half of 2020.
# 
# One could assume changed schedules due to the covid-19 outbreak. <br> A check on previous seasons (unscrapped) reveals not such overlap, but it was only done for one swimmer. An additional scrapping of other seasons is necessary.<br>The provided code supports this functionality. Scrapping was not performed because of already discussed ethical and time intensive issues as well as the fact that the objective is to simulate swim races in the next chapter.
# 
# 

# In[41]:


for season in [2020,2021]:
    dict_ = get_min_max_Date(events,season,mycol)
    print('Season %s was from %s until %s'%(season,dict_['min'],dict_['max']))


# ## Points vs Time
# 
# So far Top100 and Performance data was explored separately from this chapter on the data will be merged to enrich the exploration.
# 
# The following plot shows the relation between *time* and *points* for each gender group in 100m Freestyle on 50m courses.
# 
# Before plotting data from the sql and mongoDB databases have to be merged. The gender is stored in the sql database and the time and points in the mongoDB database.
# 
# Following observations regarding the output plot:
# * There are two distributions for male and female. It is not valid to say that male athlets are always faster than females, because there is an overlap between 52 and 54 seconds range. Male athletes simply get the same amount of points for a smaller time and vice versa.
# * There is one slow male athlete in comparision to other athletes at 61 seconds. When looking up the given name on swimrankings.net it is a young athlete starting his career.

# In[89]:


df_scatterplot = get_times_and_points(mycol,'100m Freestyle','50m')
df_sql = pd.read_sql_query('SELECT "id","name","sex","year_of_birth" FROM "swimmerData" WHERE time=\'current\'',engine)
df_sql = df_sql.astype({'year_of_birth':'int'})
df_sql['age'] = 2022 - df_sql['year_of_birth']


# In[90]:


'''
Merge of dataframes to enrich the plot with name and gender.
'''
fig = px.scatter(pd.merge(df_scatterplot,df_sql,on='id',how='inner'), x='time',y='points',color='sex',title="Scatterplot for times vs points by gender (100m Freestyle on 50m Courses)",hover_data=['name'])
fig.update_layout(
    xaxis_title="Seconds",
    yaxis_title="Points",
)
fig.show()


# ## Derive new information from Athlete's data
# 
# In this part the data for each athlete is used to generate new information.
# 
# Questions:
# * Did the athlete change events?
# * Did the athlete improve between the seasons?

# ### Athlete changes in Events
# 
# **Amount of events**
# 
# To answer the question if an athlete has changed events it is checked first if the amount of events is equal between 2020 and 2021.
# 
# It is possible that an athlete did not swim 100m Freestyle in 2020 but added it to his/her "portfolio" in 2021 - vice versa.
# This approach has the downside that it cannot identify changes where one event replaced another because the difference in events would be zero.
# 
# The following code blocks add a column *diff_events2021* to show the change of different events per athlete. The column is filled with a function call on each id and season in the mongoDB database.
# 
# The returned scatterplot shows that every athlete changed events, because no dot is printed on Zero.
# 
# While an connection between age and an increase of events could be assumend, because an athlete focussing on his/her best stroke with experience growing over time, such connections is not supported by the plot.

# In[91]:


'''
Looping through list of ids and calling the function for all events.
Then calculation the difference between 2021 and 2020 via length of lists.
id is set as index so it can be used in dataframe.loc
'''

id_list = df_sql['id'].to_list()
df_sql.set_index('id', inplace=True)
df_sql['diff_events2021'] = 0

for id in id_list:
    events_2020 = get_events_two(mycol,id,2020)['events']
    events_2021 = get_events_two(mycol,id,2021)['events']
    df_sql.loc[id,'diff_events2021'] = len(list(filter(lambda event: event not in events_2020,events_2021))) - len(list(filter(lambda event: event not in events_2021,events_2020)))


# In[92]:


fig = px.scatter(df_sql[df_sql['diff_events2021']!=0],y='age',x='diff_events2021',orientation='h',color='diff_events2021',hover_data=['name','age'])
fig.update_layout(barmode='stack', yaxis={'categoryorder':'total ascending','title':'Age'}, xaxis={'title':'Difference'},title='Difference in amount of events between 2021 and 2020')
fig.show()


# **Type of events**
# 
# The downside of the scatterplot above is that the dots for equal age and difference are overlapping and the hover method does not show athlete data below. For example Caleb Dressel is overlapped by Szebasztian Szabo. And the question on the type of events is not answered. Therefore the function get_events_two() can be called on an specific athlete for his/her unique information.
# 
# The following code block filters the events from Caeleb Dressel. In 2021 he swam a total of four additional events (in terms of stroketype!). The additional / droped events are printed below.

# In[104]:


print('Caeleb Dressel changed the amount of events by %d between 2020 and 2021.'%df_sql.loc['4772537','diff_events2021'])
Dressel_2020 = get_events_two(mycol,'4772537',2020)
Dressel_2021 = get_events_two(mycol,'4772537',2021)
print('The additional events are:',list(filter(lambda event: event not in Dressel_2020['events'],Dressel_2021['events'])))
print('The droped events are:',list(filter(lambda event: event not in Dressel_2021['events'],Dressel_2020['events'])))


# ### Improvement between seasons
# 
# **Preparing Data**
# 
# To see improvement one can compare average times for an event and course. Therefore the following code generates a pandas dataframe with average times from mongoDB data.
# 
# Notice that the head is 2020 and the tail is 2021 because of the for loop iterating over season_List in that order.
# 
# Because we learned above that there is difference in times for male and female the sql data will be merged to the new dataframe. This should enable a plot for male and female subgroups.
# It is important to mention that changes in average time do not have to be statistically significant.
# 
# 1. df_0 holds the averageTimes per season for each athlete_id
# 2. df_1 is the result of an inner merge between df_0 and df_sql from above
# 3. df_2 is the result of pivoting the season rows with avgTime values

# In[105]:


'''
This code generates a pandas dataframe for all events stored in *events* above, courses in course_List, all seasons in season_List and all ids in the *id_list* (also generated above).
It is not required as we only look for data on 100m Freestyle (50m Course)
'''

trigger = True
season_List = [2020,2021]

for season in season_List:
    for id in id_list:
        if trigger:
            trigger = False
            df_0 = pd.DataFrame.from_dict(get_avg_times(mycol,'50m','100m Freestyle',id,season))
        else:
            df_0 = pd.concat([df_0,pd.DataFrame.from_dict(get_avg_times(mycol,'50m','100m Freestyle',id,season))])

df_0 = df_0.rename(columns={'_id': 'id'})
df_0.head()


# In[110]:


df_1 = pd.merge(df_0,df_sql.reset_index()[['id','name','sex']],on='id',how='inner') # merge pandas dataframe
df_1['avgTime'] = df_1['avgTime'].astype(str).astype(float) # Convert Decimal from mongoDB to float in pandas dataframe
df_2 = df_1.pivot_table(
    values='avgTime',
    index=['id','sex','name'],
    columns='season'
    )
df_2.reset_index(inplace=True)
df_2 = df_2.dropna()
df_2['Improved'] = np.where(df_2[2021]>df_2[2020],True,False) # Numpy where adds a column with indicator of improvement.
df_2.head()


# In[123]:


print('Due to using pivot the length of df_1: %s is reduced by half and df_2 is: %s'%(len(df_1['id'].unique()),df_2.shape[0]))


# **Plot improvement between season 2021 and 2020**
# 
# While df_2 shows if an athlete did improve or not (each row on its own), a plot of total athletes by gender will be returned below.
# 
# The following plot shows that for both groups (male and female) only a minor share did improve in average time. As mentioned earlier those improvements should be checked on statistically significance. A significant information on the probability of improvement between seasons could be used in Simulations like the one in the next chapter *Simulation.*

# In[124]:


fig = px.bar(df_2.groupby(['Improved','sex']).count().reset_index(),x='id',y='Improved',orientation='h',color='sex')
fig.update_layout(yaxis={'categoryorder':'total ascending','title':'Improved'}, xaxis={'title':'Number of Athletes'},title='Number of Athletes by Gender: Improvement of average time in 100m Freestyle',hovermode=False,plot_bgcolor='#ededed')
fig.show()


# ## Additional / Open Tasks
# 
# It was planned to show the places where swim competitions took place. However, the used geopy module return strange results. For example Naples is in Italy and in South Africa. This result could be improved with further feature engineering on the raw data.
# 
# The following code block returns the map with flawed output. Please note that it is not optimized. It runs a little bit longer (4.5 minutes), partly because the RateLimiter has a delay of one second per request.
# 
# An interesting exploration might be if an athlete performs better in specific areas like Europe vs North America or Italy vs Sweden. Such investigation could provide informations on connections between traveling and performance. Another topic the *Simulation* Chapter will address.

# In[125]:


def unwind_events(event):
    pipeline = [

        {'$unwind': '$%s'%event},
        {'$group':{
        '_id':event,
        'wanted':{'$push':'$%s.Place'%event}
    }} 

    ]
    return list(mycol.aggregate(pipeline))

def events_toset(event):
    mySet = set()
    for i in unwind_events(event):
        mySet.update(i['wanted'])
    return mySet

places = set()
for event in events:
    places.update(events_toset(event))

locations = list(places)

geolocator = Nominatim(user_agent='myMac')
geocode = RateLimiter(geolocator.geocode,min_delay_seconds=1)

df_places = pd.DataFrame(locations, columns=['name'])
df_places['latitude'] = df_places['name'].apply(geolocator.geocode).apply(lambda name: name.latitude if name else None)
df_places['longitude'] = df_places['name'].apply(geolocator.geocode).apply(lambda name: name.longitude if name else None)
df_places_nonan = df_places.dropna()
df_places_nonan.reset_index(inplace=True)
df_places[df_places['latitude'].isnull()]
locdataList = df_places_nonan[['latitude','longitude']].values.tolist()
map = folium.Map(location=[float(df_places_nonan["latitude"].mean()), float(df_places_nonan["longitude"].mean())], zoom_start=2)
for point in range(len(locdataList)):
    folium.Marker(locdataList[point],popup=df_places_nonan['name'][point]).add_to(map)
map


# In[126]:


get_ipython().system('brew services stop mongodb-community@5.0')

