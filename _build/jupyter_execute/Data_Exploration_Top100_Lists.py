#!/usr/bin/env python
# coding: utf-8

# # Data Exploration Top 100 Lists

# In[2]:


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


# ## Questions
# 
# [swimrankings.net](https://www.swimrankings.net/) provides Top100 lists for athletes separated into male and female as well as current and alltime. Those categories lead to the assumption that there are currently active athletes and some in-active athletes whos past performance are still outstanding in comparision to the currently active group.
# 
# ![title](pictures/SchwimmerTop100.png)<br>(Source: [swimrankings.net](https://www.swimrankings.net/))
# 
# For those lists following questions are examined.
# 
# * Do athletes belong to both groups? At the moment no overlap is assumed.
# * How old are in-active alltimers in comparision to currently active athletes?
# * Are there more male or female in-active alltimers?
# * Which nationality do the athletes have?
# 
# ## Loading Data from SQL
# 
# Those questions are answered with the data stored in the sql database *swimmerData* which was introduced in the chapter on webscrapping.
# 
# After loading the data from sql to a pandas dataframe an overview of unique values is generated with the function examine_unique_values. Note that this is not generated for the ids and names, because they are expected to be unique and therefore equal to the length of dataframe. Remark: Off course an actual overlap is assumed to show some code.

# In[4]:


conf = connectDatabase('configPostgresSQL.json')
conn_str = 'postgresql://%s:%s@localhost:5432/%s'%(conf["user"], conf["passw"],conf["database"])
engine = sa.create_engine(conn_str)
inspector = sa.inspect(engine)

df = readSQL('swimmerData',engine)
df.head()


# In[5]:


def examine_unique_values(df):
    '''
    takes dataframe
    returns print statements on unique data in all columns that are not called 'name' and 'id'.

    if columns are called name or id, an exception is raised and the next column will be evaluated.
    '''
    notList = ['name','id']
    print('The dataframe has %d rows and %d columns.'%(df.shape[0],df.shape[1]))
    for column in df.columns:
        try:
            print('-'*20)
            if column in notList:
                raise Exception
            print('column_name:', column)
            print('values:', df[column].unique())
        except:
            print('column_name:', column)
            print('Length of List with unique values is equal to length of dataframe' if len(df[column].unique()) == df.shape[0] else 'Error: List of unique values are unequal length of dataframe.')


examine_unique_values(df)


# ## Athletes in Alltime and Current
# 
# The overview provides us with following information:
# 
# * The columns *name* and *id* are not as long as the dataframe.
# * There are athletes with *??* for the year of birth.
# 
# First the dataframe is searched for athletes with the expression *??* for year of birth. This returns one chinese athlete from the female Top 100 alltime list.
# 
# Furthermore it is shown that *name* and *id* are not unique in the length of the dataframe. Thus there must be an overlap. Maybe Jie LI's year of birth can be found in an other row, when she is in the dataframe twice?
# 
# The search for her id returns only one row. Thus row 348 is unique by id and LI, Jie occurs only once. Depending on further questions involving an athletes age the row has to be droped from the dataframe.

# In[6]:


df[df['year_of_birth'] == '??']


# In[7]:


df[df['id'] == '4044739']


# 
# Due to the the list of name's and id's unique values being not the same as the length of the dataframe those values must occure more than once. It is possible that an currently active athlete is also part of the Top100 alltime group. Which will be explored in the following code blocks.
# 
# First the duplicated ids are stored in a dataframe slice by first occurence. The code prints a random athlete from the overlapping group when it is executed.
# 
# Finally a venn diagram shows the overlap and reveals the fact that we are actually dealing with 286 athletes due to 114 athletes being in both groups.<br>
# Unexpected was the equal distribution of 86 athletes in both not overlapping groups. The sum in the venn diagram is not equal to 400 because the 114 has to be counted twice.
# 
#         400 = 86 + 114 * 2 + 86

# In[11]:


duplicate_ids = df[df.duplicated(['id'], keep='first')]
row = random.randint(0,duplicate_ids.shape[0])
id = duplicate_ids.iloc[row]['id']
print('The extracted Dataframe "duplicate_ids" includes athletes with the status %s.'%duplicate_ids['time'].unique())
print('-'*20)
print('For example following athlete occurs two times. '    'Therefore an array of two value_sets can be extracted from the Dataframe.\nOne time as currently active and one time as alltime:\n',df.loc[df['id']==id].values )
print('-'*20)
print('Answer: %d athletes belong to the group of active Top100 and alltime Top100.'%len(duplicate_ids))


# In[13]:


a = df[(df['time']=='current')]
b = df[(df['time']=='alltime')]
set1 = set(a['id'])
set2 = set(b['id'])
plt.figure(facecolor='white')
venn2([set1,set2],('Currently Active','Alltime'))
venn2_circles(subsets=[set1,set2],linestyle='dashed',linewidth=1,color='black')
plt.title('Amount of athletes belonging to a single group or both groups')
plt.show()


# ## Age of active vs inactive Athletes
# ### Preparation
# 
# Question: How old are in-active alltimers in comparision to active athletes?
# 
# First the above shown missing value is droped and a df_clean is created as deep copy. Additionally the unique values are evaluated once more and the length of the dataframe should be equal to the 286 actual unique athletes minus the removed row with missing year of birth. Thus 285 rows are expected.
# 
# The duplicated ids are removed. The first occurance of id is kept because this is the status "current" and it is needed to answer the question on age difference between both groups.
# 
# Generally it is expected that alltimers that are not active anymore are older than active athletes.

# In[14]:


df_clean = df[df['year_of_birth'] != '??'].copy(deep=True)
df_clean = df_clean.drop_duplicates(subset='id', keep='first')
examine_unique_values(df_clean)


# In order to get the athletes' ages the year of birth has to be defined as interger. This allows to perform calculations with the data. In the next step an *age* column based on the year 2022 is calculated.

# In[16]:


df_clean.info()


# In[18]:


df_clean = df_clean.astype({'year_of_birth':'int'})
df_clean['age'] = 2022 - df_clean['year_of_birth']
df_clean.info()


# ### Results Distribution Ages
# 
# Calling the describe method on the groupby of time and age presents following values. The boxplot reveals even better that the distributions for ages of currently active and alltime athletes are different.
# 
# The currently active athletes are on average younger than the athletes in the alltime list. Interestingly there is an alltime athlete with the age of 16 and this age should be considered currently active, because it is a age where swimming careers are starting to take off.

# In[13]:


df_clean.groupby('time')['age'].describe()


# In[20]:


fig = px.box(df_clean, x='age',y='time',color='time',title="Distribution by age for Top100 Subgroups",orientation='h')
fig.update_layout(
    xaxis_title="Subgroup Top100",
    yaxis_title="Age",
    plot_bgcolor='#ededed'
)
fig.show()


# Until now it was assumed that an athlete from the websites' "alltime"-table must be in-active when he is not listed in the "current"-table.<br>
# Young athletes usually are expected to be active and its confusing when an athlete of the age 16 is part of the Top100 but not in the Top100 current.
# Below the athlete is filtered with data from the boxplot.

# In[ ]:


df_clean[(df_clean['age'] == 16) & (df_clean['time']=='alltime')]


# Because of this outcome [swimrankings.net](https://www.swimrankings.net) was reviewed. It was found that the tables for current and alltime are based on alltime performances. As we already found out there are athlete on alltime that are not on current and vice versa. The statements on the website raise the question how is distinguish between those groups, when the same metric is used? The website must use a different defintion of an athletes status that is not directly accessable. Maybe an athlete has to participate in races in the onging year 2022 to be counted as active. The 16 year old Evelyn Reeder only has times for 2021 so far: [Link to Evelyn Reeders Data on swimrankings.net](https://www.swimrankings.net/index.php?page=athleteDetail&athleteId=5461897&pbest=-1)
# 
# ![](pictures/top100_description_alltime.png)
# ![](pictures/top100_description_current.png)<br>
# Source: [swimrankings.net](https://www.swimrankings.net)
# 
# 
# However, despite the overlap issue the boxplot supports an overall assumption that athletes retire in their 30s. Alternatively the overlapping distributions can be changed with an own definition. For example athletes younger than 33 are active and vice versa. This could be achieved with following code and provides the chance for switching to bool values for the status active.
# 
#     df['active'] = np.where(df['age']<34,True,False)

# ### Age of female and male athletes
# 
# Due to above outcome the question on age difference for in-active athletes by gender cannot be answered without being biased.
# 
# Instead following questions will not differ between the status. The new question is **Distribution of age for female and male athletes.**
# 
# Based on the below ploted distributions one can expect that there is no significant difference in the age distributions by gender. A t-test might verify this. Open question, not answered in this book, should only active athlete distributions be compared? But this would need a clear threshold for active and in-active athlets.

# In[21]:


df_clean.groupby('sex')['age'].describe()


# In[24]:


fig = px.box(df_clean, x='age',y='sex',color='sex',title="Distribution male and female athletes by age", orientation='h')
fig.update_layout(
    xaxis_title="Gender",
    yaxis_title="Age",
    plot_bgcolor='#ededed'
)
fig.show()


# ## Nationality of Athletes
# 
# ### Distribution of Age by Nation
# 
# Below is a first overview on the age distributions of all nations. There are athletes being the only one in the top100 lists for his/her nation. Those values are excluded from the boxplot.
# The plot reveals that for Serbia athletes of the same age exist. Those are shown in the code block beneath the plot.

# In[32]:


df_clean.groupby('nation')['age'].describe().sort_values('count',ascending=False).head()


# In[50]:


fig = px.box(df_clean.loc[df['nation'].isin(df_clean.groupby('nation')['age'].describe().reset_index()[df_clean.groupby('nation')['age'].describe().reset_index()['count']>1]['nation'].to_list())],
    x='nation',y="age",title="Distribution of age by nation")
fig.update_layout(
    xaxis_title="Nation",
    yaxis_title="Age",
    plot_bgcolor='#ededed',
    xaxis={'categoryorder':'total descending'}
)
fig.show()


# In[51]:


print('There are following athlets for Serbia.')
df_clean[df_clean['nation']=='SRB']


# 
# ### Count of Athletes by nation
# 
# A bar plot might imparts the message a bit faster (compare Hichert's *SUCCESS*-Rules), but maps can provide a huge benefit and how to plot them should be in every Data Scientists repertoire.
# 
# In the following parts the data will be prepared for plotting in a map. This includes the examination of country codes, looking up polygons for the plot and engineering some features.
# 
# Frist the values of the column *nation* are counted and stored in a dataframe. This gives the total occurence of athletes per nation.

# In[55]:


map_data = pd.DataFrame(df_clean.value_counts('nation'), columns=['count']).reset_index().copy(deep=True)
print('The columns are: %s'%map_data.columns.values)


# **Country Codes IOC vs GeoJson** 
# 
# The data from swimrankings.net uses codes according to the International Olympic Committee (IOC), which is different to the codes in the GeoJson File.
# 
# One major issue is that there are more than one National Olympic Committees for Chinese regions. In this use case it is Hong Kong which is not included in the GeoJson File for countries. In order to not get stuck in political discussions following statement from an translation office will be used to justify the transformation of Hong Kong athletes to Chinese athletes.
# 
# > "Hong Kong residents who are of Chinese descent and were born in the Chinese territories (including Hong Kong) ... are Chinese nationals. (star-ts.com: [fn1])"
# 
# In the following code block the number of Hong Konger athletes will be added to China even though Hong Kongers do not necessarily identify themself as Chinese. This transformation will only happen for this map.
# 
# The following block generates a dictionary with IOC Country Codes as Keys and the Country Names as Values.
# 
# 
# [fn1]: https://www.star-ts.com/translation/what-nationality-are-people-from-hong-kong/
# 

# In[52]:


'''Get IOC Countrycodes'''
ioc_countrycodes = pd.read_csv('https://raw.githubusercontent.com/johnashu/datacamp/master/medals/Summer%20Olympic%20medalists%201896%20to%202008%20-%20IOC%20COUNTRY%20CODES.csv')
ioc_dict = dict(zip(ioc_countrycodes['NOC'],ioc_countrycodes['Country']))
print('The value for HKG is %s'%ioc_dict['HKG'])


# The following block generates a Dictionary with Country Names as Keys and Country Codes as Values.

# In[53]:


'''Get Geojson file and create a dict where the name is key and the code is value.'''
world_geojson = requests.get('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json').json()
Dict_CountryCode = dict()
for i in world_geojson['features']:
    Dict_CountryCode[i['properties']['name']] = i['id']
print('The value for China is %s'%Dict_CountryCode['China'])


# The following block increases the Number of Chinese athletes by the Number of Hong Kong athletes and removes the Hong Kong counts from the Dataframe.

# In[56]:


val_before = map_data[map_data['nation']=='CHN']['count'].values[0]
val_before_hkg = map_data[map_data['nation']=='HKG']['count'].values[0]
map_data.loc[map_data[map_data['nation']=='CHN']['nation'].index[0],'count'] = map_data[map_data['nation']=='CHN']['count'].values[0] + map_data[map_data['nation']=='HKG']['count'].values[0]
map_data=map_data[map_data['nation']!='HKG']
val_after = map_data[map_data['nation']=='CHN']['count'].values[0]
if (abs(val_after-val_before)) == val_before_hkg:
    print('Value for China was changed from %d to %d'%(val_before,val_after))
    print('The difference is equal to the value for HKG: %d'%(val_before_hkg))
else:
    print('something went wrong - check Dataframe')
print('-'*20)
print('HKG was dropped from DataFrame: %s'%('HKG' not in map_data['nation'].values))


# Based on the above discussed dictionaries it is possible to modify the dataframe for the map.
# A lambda function is applied to the original nation column with IOC codes.
# 
# Where IOC codes are equal to GeoJson-IDs those are returned for the new column. Where the IOC codes do not match, the IOC Code is used to retrieve the country name from the dictionary and this country name is used as key for the Dictionary with GeoJson IDs.
# 
# The column nation_checked has the GeoJson-IDs which are used for the map.

# In[57]:


def countrycode(code,dict,own_ioc_dict):
    '''
    takes a code, a dictionary and a second dictionary
    returns code depending on being in dictionary

    compares if code is in values from first dictionary,
    if True the code is returned
    if False the code will be used as key to retrieve a countryname(value) from the second dictionary.
    this value will be used as key in the first dictionary to return a proper code.

    '''
    if code in dict.values():
        return code
    else:
        return dict[own_ioc_dict[code]]

map_data['nation_checked'] = map_data['nation'].apply(lambda nation: countrycode(nation,Dict_CountryCode,ioc_dict))
print('Columns are now',map_data.columns) 


# **Map Plot**
# 
# In a first approach the 'world_geojson'-object from above was used for the map. But it did not support the chance to provide a hover functionality. Therefore the next code block reads the json into a *GeoPandas-Dataframe.*
# 
# The GeoPandas-Dataframe holds polygon-data in the geometry column to plot shapes on a map. This dataframe is merged with the map_data-dataframe which holds the counts of athletes. The id column is used for merge on nation_checked. *Note: The renaming could have been performed before.*

# In[58]:


'''create a geo-dataframe with geopandas.'''
geoJSON_df = gpd.read_file('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json')
geoJSON_df = geoJSON_df.rename(columns={'id':'nation_checked'})


# In[59]:


final_df = geoJSON_df.merge(map_data, on='nation_checked').drop('nation',axis=1).rename(columns={'nation_checked':'nation'})
final_df.head()


# The following code block generates a map which shows the count of athlete by nation.
# 
# The map shows that the world elite in swimming is dominated by athletes born in the United States of America. Followed by Australia with less than half of the amount from the USA.

# In[60]:


m = folium.Map(location=[45,10],zoom_start=2) #Location ist Mittelpunkt von Nordamerika

folium.Choropleth(
    geo_data=final_df,
    data=final_df,
    columns=['nation','count'],
    key_on='feature.properties.nation',
    fill_color="BuGn",
    fill_opacity=1,
    legend_name="Amount of athletes in data",
    nan_fill_opacity=0,
    overlay=True
).add_to(m)


#Add hover functionality.
style_function = lambda x: {'fillColor': '#ffffff', 
                            'color':'#000000', 
                            'fillOpacity': 0.1, 
                            'weight': 0.1}
highlight_function = lambda x: {'fillColor': '#000000', 
                                'color':'#000000', 
                                'fillOpacity': 0.50, 
                                'weight': 0.1}
hover = folium.features.GeoJson(
    data = final_df,
    style_function=style_function, 
    control=False,
    highlight_function=highlight_function, 
    tooltip=folium.features.GeoJsonTooltip(
        fields=['name','count'],
        aliases=['Nation','Number of Athletes'],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
    )
)
m.add_child(hover)
m.keep_in_front(hover)

#Add light design layout
folium.TileLayer('cartodbpositron').add_to(m)

# m.save('Number_of_Athletes_per_Country.html')
m

