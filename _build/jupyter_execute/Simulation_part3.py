#!/usr/bin/env python
# coding: utf-8

# # Best Athlete of Event - Simulation

# In[1]:


from myfunc import *
from myclasses import *
from mysimfunc import *
import itertools
from pymongo import MongoClient
import sqlalchemy as sa
import plotly.express as px
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from plotly.offline import init_notebook_mode
init_notebook_mode() # To show plotly plots when notebook is exported to html


# In[2]:


get_ipython().system('brew services start mongodb-community@5.0')


# In[3]:


client = MongoClient()
client = MongoClient('mongodb://localhost:27017/')
mydb = client['swimmerData']
mycol = mydb.get_collection('performance')
conf = connectDatabase('configPostgresSQL.json')
conn_str = 'postgresql://%s:%s@localhost:5432/%s'%(conf["user"], conf["passw"],conf["database"])
engine = sa.create_engine(conn_str)
inspector = sa.inspect(engine)


# In[4]:


df_sql_male = pd.read_sql_query('SELECT "id","name" FROM "swimmerData" WHERE time=\'current\' AND sex=\'m\'',engine)
male_athlete_ids = list(df_sql_male.itertuples(index=False,name=None))


# In the following code blocks option No 4 from the Chapter *Best Athlete of Event - Time Complexity* is performed.

# In[6]:


injured = True
DictAthleteObjects2 = generate_objects(male_athlete_ids,mycol,'200m Backstroke','50m',injured)

for race_participants in itertools.combinations(list(DictAthleteObjects2.keys()),8): 
    '''
    Following code performs simulation based on functions in code block above.
    The code simulates 10k races and triggers each objects' placement tracking via the functions.
    '''
    for i in range(10000):
        award_ceremony(swim_race(race_participants,DictAthleteObjects2),DictAthleteObjects2,injured)   


# In[7]:


athlete_keys = list(DictAthleteObjects2.keys())
'''
Following code stores simulation results in a List of Dictionaries which is later loaded into a pandas dataframe.
'''
myList = []
if injured:
    for j in athlete_keys:
        myDict = {}
        myDict['name']=DictAthleteObjects2[j].get_name()
        myDict['id']=DictAthleteObjects2[j].get_id()
        myDict['total']=DictAthleteObjects2[j].get_placement_ratio(1,ratio_type='total')
        myDict['fit']=DictAthleteObjects2[j].get_placement_ratio(1,ratio_type='fit')
        myDict['injured']=DictAthleteObjects2[j].get_placement_ratio(1,ratio_type='injured')
        myList.append(myDict)
else:
    for j in athlete_keys:
        myDict = {}
        myDict['name']=DictAthleteObjects2[j].get_name()
        myDict['id']=DictAthleteObjects2[j].get_id()
        myDict['total']=DictAthleteObjects2[j].get_placement_ratio(1,ratio_type='total')
        myList.append(myDict)
'''
Following code builds a horizontal bar plot for simulation results, where first place probabilty is larger than 0.
'''
df = pd.DataFrame.from_dict(myList)
df = df[df['total']>0]
if injured:
    title_info = 'Probability of 1st Place per athlete by health'
    fig = px.bar(df,y='name',x=['fit','injured'],orientation='h',title=title_info)
    fig.update_layout(yaxis={'categoryorder':'total ascending'},xaxis={'title':'Probability'},title_font_size=15,plot_bgcolor='#ededed')
    fig.show()
else:
    title_info = 'Probability of 1st Place per athlete'
    fig = px.bar(df,y='name',x=['total'],orientation='h',title=title_info)
    fig.update_layout(yaxis={'categoryorder':'total ascending'},xaxis={'title':'Probability'},title_font_size=15,plot_bgcolor='#ededed')
    fig.show()


# ## Interpreting results for all possible combinations and Prospects
# 
# The plot above can be interpreted as the earlier presented examples above (Now in Chapter *Introduction to Simulation*). This time it is a probability after all possible combinations for competitors where iterated. Thus Evgeny Rylov is the most successfull athlete in 200m Backstroke based on the assumptions for this simulation. This is also supported by the mean of his normal distribution, which is displayed in the boxplot below. It is the lowest mean for all male athletes in the 200m Backstroke event.
# 
# As described earlier it was expected that the athlete with the lowest mean is going to win the most times. But the athlete objects also keep track of other placements. Thus the Monte-Carlo-Simulation simulates probabilities of specific placements and with that information for example the probability of not being under the first three places can be calculated. Therefore Evgeny Rylov is closer evaluated.
# 
# Interestingly Robert Glinta never makes first place despite a very small distribution in the middle field of box plots. When he has the luck of swimming faster than the favoirtes with smaller means, he still gets "overtaken" by other athletes - in this simulation.

# In[8]:


myList = []
myNames = []
myDict={}
for key in athlete_keys:
    array = get_array_times(mycol,'50m','200m Backstroke',key)
    myDict[DictAthleteObjects2[key].get_name()]=pd.Series(np.random.normal(np.mean(array),np.std(array),size=10000))
df1 = pd.DataFrame(myDict)
fig = px.box(df1,orientation='h')
fig.update_layout(yaxis={'categoryorder':'total descending'},title_text='Boxplot for distributions in 200m Backstroke (male athletes on 50m course)',plot_bgcolor='#ededed')
fig.show()


# The plot below shows the probability for each placement in the 200m Backstroke tournaments for Evgeny Rylov. Note that the yaxis has a logarithmic scale. Low placements are places of high numerical value. Thus 1 is a high place and 8 the lowest place.
# 
# It can be seen that the probabilities for low placements are decreasing ovarall.<br>
# Due to the logarithmic scale it can be misleading, but shall not be said that the most injuries are related to low placments. Instead it is valid to say that the share of injury occurences rises for lower placements.
# 
# For the print statement beneath the plot:
# * Based on the placements for each athlete the probability of missing the winners' podium can be calculated. (or other scenarios of interest)
# * The logarithmic scale hides the fact that for injuries a uniform distribution with probability of 50 % was used and the red areas are actual amost the same size as the blue areas.
# 
# Thus the injuries are simulated as expected, even though deeper evaluation is not necessary. Due to the design we know that around half of the races the athlete will be injured.
# 
# 
# ## Prospect for Use Cases
# 
# However Monte-Carlo-Simulation could enable to generate sample distributions for more complex conditions of randomness and to verify if those are statistically significant different. Beneath print statement shows the amount of races Evgeny Rylov participated in during the simulation. This amount of samples would not exist for real data and shows a benefit of Monte-Carlo-Simulation.
# 
# It is imagined that an athletes' training diaries holds a lot of data to exermine situations with random events implying a connection to certain outcomes.
# 
# For example having a good nights sleep in the hotels before race day. To improve the use case such insights are needed. In best case an athlete might be less stressed and more focussed when knowing that his/her personal data showed no significant difference for sleeping seven instead of eight hours.
# 
# The simulation could also be enriched with a time component to simulation issues over time. For example the simulated injury could affect the athlete for a couple of races in the provided classes. Thinking in real data there might be a possibility to get a probability for training improvements of competitors between seasons or long time effects of an injury due to missed training. Finally, to identify such Use Cases sport scientist might provide good guidance.

# In[9]:


id = pd.read_sql_query('SELECT "id" FROM "swimmerData" WHERE name=\'RYLOV, Evgeny\' AND time=\'current\'',engine).values.item()

df_rylov = pd.merge(
    pd.DataFrame.from_dict([DictAthleteObjects2[id].get_placement_injured()]).unstack().reset_index().drop(columns='level_1').rename(columns={'level_0':'Place',0:'Count_injured'}),
    pd.DataFrame.from_dict([DictAthleteObjects2[id].get_placements()]).unstack().reset_index().drop(columns='level_1').rename(columns={'level_0':'Place',0:'Count'}),
    on='Place')
df_rylov['Probability_healthy'] = (df_rylov['Count']-df_rylov['Count_injured'])/df_rylov['Count'].sum()
df_rylov['Probability_injured'] = df_rylov['Count_injured']/df_rylov['Count'].sum()
df_rylov['Place'] = df_rylov['Place'].astype(str)


fig=px.bar(df_rylov,x='Place',y=['Probability_healthy','Probability_injured'],log_y=True)
newnames = {'Probability_healthy': 'healthy', 'Probability_injured': 'injured'}
fig.for_each_trace(lambda t: t.update(name = newnames[t.name],legendgroup = newnames[t.name],hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))
fig.update_layout(title_text='Evgeny Rylov\'s probabilities for Placement by health status',yaxis={'title':'Probability (Log Scale)'},plot_bgcolor='#ededed')
fig.show()


# In[10]:


print('The probability of missing the winners\'s podium is %s %%.'
    %("{:.2f}".format(np.sum((df_rylov[(df_rylov['Place']!='1') & (df_rylov['Place']!='2') & (df_rylov['Place']!='3')][['Probability_healthy','Probability_injured']].values))*100)))
print('The total share of races when injured is: %s %%'%("{:.2f}".format((df_rylov['Count_injured'].sum()/df_rylov['Count'].sum())*100)))
print('Evgeny Rylov participated in %s simulated races.'%"{:.0f}".format(df_rylov['Count'].sum()))


# In[11]:


get_ipython().system('brew services stop mongodb-community@5.0')

