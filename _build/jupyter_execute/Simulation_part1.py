#!/usr/bin/env python
# coding: utf-8

# # Introduction to Simulation

# In[1]:


from myfunc import *
from myclasses import *
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


# ## General Thoughts
# Usually eight athletes compete for Gold in a swim race. Thus the probability of any athlete winning gold is 1/8.
# 
# However the probability of an athlete winning gold is not totaly random. It is more based on an athletes' performance, training status and health.
# Thinking of swimmers as machines without gut feeling, sleeping issues or whatsoever, and those machines beeing on the same performance level, would support the 1/8 probability of winning first place in a race. Actually every swimmer has his own unique abilities in dealing with stress and competitivness as well as own training concepts. Therefore each swimmer has to be evaluated on his own. But how can one determine the probability of an athlete winning first place?
# 
# Unfortunately we cannot let the athlete race an infinite time to get enough samples for a valid statement. This lag of data (one race = one sample outcome) and the randomness in events like bad sleep, injuries or other factors can be approached with a Monte-Carlo-Simulation. This is a technique to predict probability of an uncertain event due to randomness.
# 
# ### Assumptions for Simulation 
# Thus Monte-Carlo-Simulation is an approach to predict outcome of races. But what data can be feed to the simulation?
# 
# In order to predict the outcome the past performance is utilized. Usually every athlete has his/her personal best time and one can say that the athlete with the smallest best time is the favorite for first place. However, this project uses the normal distribution, which is know to be very common in nature. This means from the data a normal distribution between the min and max value is assumed, which leads to additional assumptions as follows.
# 
# * No change in performance over time.
# * Athletes will not out- or underperform own distribution.
# * All athletes are valid to compete against each other.
# 
# The following graph shows the distributions for selected athletes. Based on the past performance and above discussed assumptions, it is possible to say that the red athlete will always win against the green athlete. The lines for the red, yellow and blue athletes overlap. Thus it might be expected that the yellow athlete will win more often against blue than red.
# 
# However, due to small overlap of red and yellow there is a very small chance of yellow winning against red. Thanks to the zoom in plotly graphs the overlap can be examined closer. This shows that also blue has a slight chance of winning against red.
# 
# The code block after the plot shows the actual values and reveals that the plottet distributions are kind of misleading. Plottet are density lines on base of a few values. Especially the green athlete has only two values, which are not enough for a fair distribution. Additionally based on the actual sample values of yellow it can be seen that guesses from actual array values would lead to yellow winning over blue far more often compared to an normal distribution. A yellow bell curve would much more overlap with blue.
# 
#  For the simulation a normal distribution between each athletes min and max value will be assumed. This leads to a bias for athletes like yellow who has far more smaller values than blue. 

# In[4]:


'''
globals() is used to enrich the plot with group_labels
'''
group_labels = ['athlete_mid2','athlete_mid1','athlete_high','athlete_small']
id_List = ['4764048','4070048','4467296','5364206']
id_List_backup = copy.deepcopy(id_List)
hist_data = []

for i in group_labels:
    globals()[i] = get_array_times(mycol,'50m','100m Freestyle',id_List.pop(-1))
    hist_data.append(globals()[i])

fig = ff.create_distplot(hist_data, group_labels, show_hist=False, show_rug=False)
fig.update_layout(title_text='Distributions of past performance for selected athletes in 100m Freestyle on 50m Course',plot_bgcolor='#ededed')
fig.show()


# In[5]:


print('-'*4,'actual values above lines are drawn on','-'*4)
print('athlete_small:',athlete_small,'\nathlete_high:',athlete_high,'\nathlete_mid1:',athlete_mid1,'\nathlete_mid2:',athlete_mid2)


# ### Generate normal distributions
# 
# Using numpy.random.normal it is possible to generate an normal distribution based on the sample data from above. Creating an array of 15000 values for each athlete returns following plot. It shows that red, yellow and blue might have a chance against each other, with red still being the favorite. Unfortunately in this simulation context there are no prices to be won by green, when competing against red, yellow and blue.
# 
# ***Important disclaimer***
# 
# *Due to the nature of normal distributions in the long run (e.g. for 15000 simulated races) the athlete with the lowest mean will be the most successful. This insight makes the simulation redundant, because the athlete with the lowest mean is the best athlete. However, this is a coding project and the code design allows to change the normal distribution approach to actual values in the object athlete class.*<br>
# *Thus such simulation might be used on more data points that where originally scrapped. For example a coach with access to training data can perform simulations on real data, where distribution is not necessarily normal. For example the yellow athlete in the plot above could have a positively skewed distribution (linkssteile Verteilung) hidden in missing data points.*
# 
# Due to this disclaimer the question for the Monte-Carlo-Simulation will be changed to "What is an athletes probability of an specific placement?"

# In[6]:


group_labels = ['athlete_mid2','athlete_mid1','athlete_high','athlete_small']
id_List = ['4764048','4070048','4467296','5364206']
id_List_backup = copy.deepcopy(id_List)
hist_data = []

for i in group_labels:
    globals()[i] = get_array_times(mycol,'50m','100m Freestyle',id_List.pop(-1))
    data = np.random.normal((np.min(globals()[i])+np.max(globals()[i]))/2,np.std(globals()[i],ddof=1),15000)
    hist_data.append(data)

fig = ff.create_distplot(hist_data, group_labels, show_hist=False, show_rug=False)
fig.update_layout(title_text='Distributions of assumed normal distribution from sample "past performance" for selected athletes in 100m Freestyle on 50m Course',plot_bgcolor='#ededed')
fig.show()


# ### Examine Conflict between Asumptions and Normal Distributions
# 
# More important is the fact that the plotted distributions provide values outside of the min and max values, which is in conflict with the made assumptions.
# 
# **No change in performance over time**
# 
# This assumptions where set on the basis that the size of data sample should not be reduced by distinguishing between seasons. Otherwise there would be two density plots per athlete, one for each season, generated by even less data points.
# 
# **Athletes will not out- or underperform own distribution**
# 
# The assumption that an athlete will not out- or underperform the min and max values was derived from the context that we only have data from swim meets (so are competition events called). Thus it is not know if an athlete swam a better or slower time compared to his training activities. Thanks to the normal distribtion overlapping the min and max values, this assumption can be softened in the way that an athlete can out- or underperform but this does not have to be the full picture due to missing data on training times. Without the training data it is not possible to say if an athlete is out- or underperforming training time distributions.
# 
# **No Age Groups**
# 
# The assumption that all athletes are allowed to compete against each other despite being in different age groups is madeup because I forgot to explore this in Data Exploration. Such subgroups could be generated when the required data from the sql database gets loaded later in this notebook.
# 
# ### Utilizing normal distributions
# 
# So far we have a method to return normal distributed values in our simulation. But it is still possible to derive the answer via other statistically tests. Looking at above graph one could expect that in a race of those four athletes the red athlete will have the highest probability of winning.
# 
# To satisfy the randomness in the Monto-Carlo-Simulation the introduced idea of an athlete feeling unwell, being injured or stress is applied. In the simulation this will be achieved with madeup values, assuming the probability of swimming injured being 50 %. At this point *injured* stands for any imaginable disadvantage. It is assumed that the injury will change the min value to the mean value of the distribution.
# 
# ***Digression:*** *Those values are made up and might be replaced and maybe more personalised with guidance from a sport scientist or actual coach. One benefit of object oriented programming is being able to set unique thresholds or conditions for athletes.*
# 
# Following plot shows that the distribution for the athlete "yellow" (from the plot above) has moved from left to the right, when the mean of the sample is used as min value. Notice that the orignal standard deviation is used and the bell curves' width neither decreased or increased. The plot below suggests that the distribition might not be statistically significant different from the healthy distribution. A t-Test could be applied to assure this. However this, as will be shown below in *Comparing Top Athletes* this does not have to be the same situation for all athletes and depends on the standard deviation.

# In[7]:


y = get_array_times(mycol,'50m','100m Freestyle','4070048')
data1 = np.random.normal(np.mean(y),np.std(y,ddof=1),10000)
data2 = np.random.normal((np.mean(y)+np.max(y))/2,np.std(y,ddof=1),10000)
fig = ff.create_distplot([data1,data2],group_labels=['healthy','injured'],show_rug=False,show_hist=False,colors=['#ff8c00', '#ff8c00'])
fig.update_layout(title_text='Athlete Yellow\'s distribution when healthy or injured',plot_bgcolor='#ededed')
fig.update_traces(patch={"line": {"dash": 'dot'}}, selector={"legendgroup": "injured"})
fig.show()


# ### Introduction of classes
# 
# As the Data Exploration showed, the 100m Freestyle events are most favoured by athlets. Thus there are the most distributions in form of athletes. To perform the Simulation of 100m Freestyle races on 50m course the required data is load from mongoDB database during initialization of on object from the class athlete.<br>
# *Notice that this class is imported from the file **myclasses.py** The class is separately discussed in the chapter **File MyClasses** of this jupyter book.*
# 
# **Athlete Class**
# 
# The idea is that for each athlete an object will be initialized and "equipped" with the data. The object has a swim method that returns a single value from the above discussed distributions. Additionally each objects holds a dictionary to keep track of the achieved placement. This tracker will be increased with the methode add_placement(). For evaluation the methode get_placement_ratio() returns the ratio of achieved placement divided by total races. The add_placement and get_placement_ratio methods are called with the placement of interest as key. Thus if an athlete object got the second place the placement count for second place will be increased and returned when requested with get_placement_ratio.<br>
# Those methods will be heavily used in the simulation and therefore were slightly described above. There are other methods like get_name() and get_id() which are discribbed in the *File MyClasses* Chapter.
# 
# **Imperfect Athlete Class**
# 
# The class *imperfect* athlete is a child class from the athlete class. It is used to simulate different behavior when the earlier described injured condition has to be evaluated. This enables to run the simulation with or without the randomness of injury. Additionally to the athlete class methods there is the tracking systems of placement when injured and a swim method which returns a single value based on discussed probability of 50 % for being injured.
# 
# 

# ### Preparing Athlete objects' data
# 
# **Names and IDs**
# 
# In the Data Exploration it was shown that the performance of male and female is distinguished by points for time. Even though the distributions overlap in the middle the "best" female will never win against the "best" male in this simulation. Therefore the data for male and female athletes is loaded into two different dataframes and each row transfered into a list.
# 
# Those lists will be iterated when the instances of athlete class objects are initialized. As we already now from Data Exploration, there are 100 female and 100 male athletes with the status current.

# In[8]:


df_sql_female = pd.read_sql_query('SELECT "id","name" FROM "swimmerData" WHERE time=\'current\' AND sex=\'f\'',engine)
df_sql_male = pd.read_sql_query('SELECT "id","name" FROM "swimmerData" WHERE time=\'current\' AND sex=\'m\'',engine)
female_athlete_ids = list(df_sql_female.itertuples(index=False,name=None))
male_athlete_ids = list(df_sql_male.itertuples(index=False,name=None))

print('There are %s female and %s male athletes loaded'%(len(female_athlete_ids),len(male_athlete_ids)))
print('-'*10,'Head of Female DataFrame','-'*10)
print(df_sql_female.head())
print('\n','-'*10,'Head of Male DataFrame','-'*10)
print(df_sql_male.head())


# **Performance Data**
# 
# According to belows mongoDB query there are 110 athletes who have competed in either 100m Freestyle or 100m Freestyle Lap on 50m courses. Thus not every ID is ligit for the simulation.
# By loading 100m Freestyle Lap the sample will be enriched with a view more data points for some athletes.
# 
# However, considering belows print statement not every athlete in the list will be considered for the simulation.

# In[9]:


query1 = {
    '$or':[{
        '$and':[
            {'100m Freestyle':{'$exists':True}},
            {'100m Freestyle.Course':'50m'}],
        '$and':[
            {'100m Freestyle Lap':{'$exists':True}},
            {'100m Freestyle.Course':'50m'}]
        }]
}

print('There are documents for %s athletes who swam 100m Freestyle on 50m courses.'%mycol.count_documents(query1))


# ## Perform Simulation
# 
# The next two code blocks will perform the simulation.
# 
# The function simulation will call further functions as described in the docstrings.
# 
# Generally the simulation will create single races by random groups of eight athletes and show results in a plot and return a dictionary of athlete class objects.
# 
# 

# In[10]:


'''
This code is not in myfunc.py because the functions below are too unique and of no use for Data Exploration.
However, due to the necessary split of this notebook, other Simulation chapters will import those functions from a mysimfunc.py File.
'''

def generate_objects(myList,collection,event,course,injured=False):
    '''
    takes myList with list of ids (as strings), collection as reference to mongoDB collection, event as string, course as string
    injured is bool to decide the kind of objected that is wanted.
    returns a dictionary of objects with athlete id as key and object as "value".

    The ValueErrer exception captures objects where min and max are equal. Thus it would be a degenerate distribution (Einpunktverteilung).
    The IndexError exception captures every objects that does not provide data for the requested event and course.
    '''
    DictAthleteObjects = {}
    for i in myList:
        try:
            if injured:
                DictAthleteObjects[i[0]] = imperfect_athlete(i,collection,event,course)
            else:
                DictAthleteObjects[i[0]] = athlete(i,collection,event,course)
        except ValueError:
            pass
        except IndexError:
            pass
    return DictAthleteObjects
    
def get_randomSample_participants(myList):
    '''
    takes a list of athlete ids (any length)
    returns a list of eight athlete ids
    '''
    outList = []
    while len(outList) < 8:
        rand = np.random.randint(0,len(myList)-1)
        outList.append(myList[rand]) if myList[rand] not in outList else None
    return outList

def swim_race(myList,ref_Dict):
    '''
    takes a list of 8 swimmers and a dictionary with objects
    returns a list of tuples with athlete id and time

    function calls the swim method of each provided object and stores the result with an id and time in a tuple.
    '''
    outList = []
    for i in myList:
        swim = ref_Dict[i].swim()
        outList.append((i,swim[0],swim[1]))
    return outList

def award_ceremony(myList,ref_Dict,injured=False):
    '''
    takes a sorted list of results for 8 athletes (ascending sort) and a dictionary with objects

    The provided list will be sorted ascending.
    The while loop is poping the last element of the list. Thus the 8th place of the race.
    Via execution of the add_placement for each object the placement counter will be increased.
    '''
    myList.sort(key=lambda athlete: athlete[1])
    while len(myList)>0:
            athlete = myList.pop(-1)
            ref_Dict[athlete[0]].add_placement(len(myList)+1,injured=athlete[2])

def list_to_string(myList):
    '''
    to create proper title in plot below
    '''
    return ' and '.join(myList)


# In[11]:


'''
This is the actual simulation, designed as function.
However each function within can be called on its own (see code block above).
'''

def simulate(collection,event,course,female_race=True,injured=False):
    '''
    takes the reference to mongoDB collection via pymongo object, event as string, course as string, female_race as bool, injured as bool
    shows a horizontal bar plot for simulation results, where first place probabilty is larger than 0.
    return the dictionary holding the athele class objects and a list of ids that participated in the race.

    remark: it is kind of inefficient that objects are generated but not used.
    
    Further details in docstrings between code, unusual but usually the simulation is not in a function.
    Benefit of function is ability to plot different races with only one line of code for more overview in notebook.
    
    First a dictionary of athlete objects is generated with id as key.
    '''
    DictAthleteObjects={}
    race_participants=[]

    if female_race:
        DictAthleteObjects = generate_objects(female_athlete_ids,collection,event,course,injured)
    else:
        DictAthleteObjects = generate_objects(male_athlete_ids,collection,event,course,injured)

    # print('%s objects generated'%(len(DictAthleteObjects.keys())))

    '''
    Following code generates a random group of 8 athlete who compete against each other.
    User could skip this part and generate his own list with 8 ids.
    '''
    race_participants = get_randomSample_participants(list(DictAthleteObjects.keys()))

    '''
    Follwing code prints the favorite and the outsider of the case. Expectation based on min values.
    '''
    iterable =(DictAthleteObjects[i].get_min_max()[0] for i in race_participants)
    seq = np.fromiter(iterable,dtype=float)
    print('Based on lowest min value, the favorite is:',DictAthleteObjects[race_participants[seq.argmin()]].get_name())
    print('Based on highest min value, the outsider is:',DictAthleteObjects[race_participants[seq.argmax()]].get_name())

    '''
    Following code deletes objects that are not participating in the race.
    '''
    for i in list(filter(lambda id: id not in race_participants,list(DictAthleteObjects.keys()))):
        DictAthleteObjects.pop(i,None)

    '''
    Following code performs simulation based on functions in code block above.
    The code simulates 10k races and triggers each objects' placement tracking via the functions.
    '''
    for i in range(10000):
        award_ceremony(swim_race(race_participants,DictAthleteObjects),DictAthleteObjects,injured)


    '''
    Following code stores simulation results in a List of Dictionaries which is later loaded into a pandas dataframe.
    '''
    myList = []
    if injured:
        for j in race_participants:
            myDict = {}
            myDict['name']=DictAthleteObjects[j].get_name()
            myDict['id']=DictAthleteObjects[j].get_id()
            myDict['total']=DictAthleteObjects[j].get_placement_ratio(1,ratio_type='total')
            myDict['fit']=DictAthleteObjects[j].get_placement_ratio(1,ratio_type='fit')
            myDict['injured']=DictAthleteObjects[j].get_placement_ratio(1,ratio_type='injured')
            myList.append(myDict)
    else:
        for j in race_participants:
            myDict = {}
            myDict['name']=DictAthleteObjects[j].get_name()
            myDict['id']=DictAthleteObjects[j].get_id()
            myDict['total']=DictAthleteObjects[j].get_placement_ratio(1,ratio_type='total')
            myList.append(myDict)

    '''
    Following code builds a horizontal bar plot for simulation results, where first place probabilty is larger than 0.
    '''
    df = pd.DataFrame.from_dict(myList)
    group_list = df['name'].to_list()
    #group_names = list_to_string(df['name'].to_list())
    group_names = list_to_string(group_list[0:4])+'<br>and '+list_to_string(group_list[4:9])
    df = df[df['total']>0]
    if injured:
        title_info = 'Probability of 1st Place per athlete by health in Group:<br>' + group_names
        fig = px.bar(df,y='name',x=['fit','injured'],orientation='h',title=title_info)
        fig.update_layout(yaxis={'categoryorder':'total ascending'},xaxis={'title':'Probability'},title_font_size=15,plot_bgcolor='#ededed')
        fig.show()
    else:
        title_info = 'Probability of 1st Place per athlete in Group:<br>' + group_names
        fig = px.bar(df,y='name',x=['total'],orientation='h',title=title_info)
        fig.update_layout(yaxis={'categoryorder':'total ascending'},xaxis={'title':'Probability'},title_font_size=15,plot_bgcolor='#ededed')
        fig.show()
    return DictAthleteObjects


# In[12]:


simDict_1 = simulate(mycol,'100m Freestyle','50m',female_race=True,injured=True)


# In[13]:


simDict_2 = simulate(mycol,'100m Freestyle','50m',female_race=False,injured=True)


# In[18]:


simDict_3 = simulate(mycol,'100m Backstroke','50m',female_race=True,injured=True)


# The plots only show values above 0. The returned dictionaries can be used to access the athlete objects.

# In[19]:


print('-'*5,'Keys from Simulation','-'*5)
for i in range(3):
    print('Keys from Simulation No %i: %s'%(i+1,list(dict.keys(globals()['simDict_'+str(i+1)]))))


# In[20]:


print('-'*5,'Participants in Simulation No 3','-'*5)
for i in simDict_3.keys():
    print(simDict_3[i].get_name())


# ### Interpreting Simulation Results
# 
# Each simulation is performing 10.000 races, which is a large amount of sample races.
# 
# Above plots show the probability of an athlete winning a race. Due to code design above code blocks can be triggered and return a different result everytime. Therefore a screenshot will be used for further discussion.
# 
# According to the screenshot below the favorite is David Popovici. He won 36 % of all races. 24 % while being healthy and 12 % while being injured.<br>
# Despite being the favorite the simulation does not return the highest probability for him. Vladislav Grinev has the highest probability of winning by 41 %.
# 
# At this point it could be possible that Grinev always won where Popovici was injured. To answer this the simulation has to be redesigned so that Popovici is always injured. But, as discussed earlier such redesign is not necessary because the evaluation of the mean is providing the result.<br>
# Instead both athletes will be analysed in detail, to explain self-fulfilling prophecy due to the desginflaw in asking for the probability of winning a race.
# 
# Furthermore the screenshot shows high values even though the athletes where injured. This comes from the uniform distribution with a 50 % probability for injury and to be fair, a really small influence by moving the min value to the mean. Indicationg an underestimated influence of the injuries.
# 
# ![title](pictures/example_simulation_favorite_notFirst.png)
# 
# 

# ### Comparing Top Athlets
# 
# In order to analyse Grinev and Popovici the distributions are plotted below. Additionally the mean, min and max values are printed.
# 
# The plot shows continuous and doted lines. Continuous lines are for the actual distribution. Doted lines represent the distribution for injuries.
# 
# Both athletes have almost the same mean with a difference of 0.1 seconds. The biggest difference is the standard deviaton. Griven's distributions are steeper and less spread, which comes from the smaller standard deviation.
# 
# Looking at the distributions it is possible to say that Popovici might be the favorite in terms of min value, but the larger standard deviation represents less consistency. Therefore Grinev with almost the same mean, but less standard deviation wins more often.
# 
# Additionally above screenshot and belows plot reveal the fact that the probability of an athlete winning in the long run is related to *the regression to the mean* in normal distributions.

# In[21]:


Popovici = get_array_times(mycol,'50m','100m Freestyle',df_sql_male[(df_sql_male['name']=='POPOVICI, David')]['id'].values[0])
Grinev = get_array_times(mycol,'50m','100m Freestyle',df_sql_male[(df_sql_male['name']=='GRINEV, Vladislav')]['id'].values[0])

Pmean = np.mean(Popovici)
Pmin = np.min(Popovici)
Pmax = np.max(Popovici)
Pstd = np.std(Popovici,ddof=1)
Gmean = np.mean(Grinev)
Gmin = np.min(Grinev)
Gmax = np.max(Grinev)
Gstd = np.std(Grinev,ddof=1)

print('-'*10,'Popovici','-'*10,'\nmean:%s\nmin:%s max:%s'%(Pmean,Pmin,Pmax))
print('-'*10,'Grinev','-'*10,'\nmean:%s\nmin:%s max:%s'%(Gmean,Gmin,Gmax))

# High number of size = 50000 to assure that vline mean is ploted with maximum turning point.
Ph = np.random.normal(Pmean,Pstd,50000)
Gh = np.random.normal(Gmean,Gstd,50000)
Pi = np.random.normal((Pmean+np.max(Popovici))/2,Pstd,50000)
Gi = np.random.normal((Gmean+np.max(Grinev))/2,Gstd,50000)

fig = make_subplots(rows=2,cols=1,shared_xaxes=True,subplot_titles=['David Popovici','Vladislav Grinev'])
fig2 = ff.create_distplot([Ph,Pi,Gh,Gi],group_labels=['healthy','injured','healthy','injured'],show_rug=False,show_hist=False,colors=['#5D7F32', '#876FA5'])

fig.add_trace(go.Scatter(fig2['data'][0],
                         line=dict(color='blue', width=0.5), legendgroup='healthy'
                        ), row=1, col=1)

fig.add_trace(go.Scatter(fig2['data'][1],
                         line=dict(color='red', width=0.5),legendgroup='injured'
                        ), row=1, col=1)

fig.add_trace(go.Scatter(fig2['data'][2],
                         line=dict(color='blue', width=0.5), legendgroup='healthy',showlegend=False
                        ), row=2, col=1)

fig.add_trace(go.Scatter(fig2['data'][3],
                         line=dict(color='red', width=0.5),legendgroup='injured',showlegend=False
                        ), row=2, col=1)
fig.update_yaxes(range=[0,1])
fig.update_layout(title_text='Distributions for David Popovici and Vladislav Grinev',plot_bgcolor='#ededed')
fig.update_traces(patch={"line": {"dash": 'dot'}}, selector={"legendgroup": "injured"})
fig.add_vline(x=Pmin, line_width=1.5, line_dash="dash", line_color='#388A73',annotation_text='min:%s'%round(Pmin,1),annotation_position='top left',row=1,col=1)
fig.add_vline(x=Pmax, line_width=1.5, line_dash="dash", line_color='#388A73',annotation_text='max:%s'%round(Pmax,1),row=1,col=1)
fig.add_vline(x=Pmean, line_width=1.5, line_dash="dash", line_color='#444614',annotation_text='mean:%s'%round(Pmean,2),annotation_position='bottom right',row=1,col=1)
fig.add_vline(x=Gmin, line_width=1.5, line_dash="dash", line_color='#388A73',annotation_text='min:%s'%round(Gmin,1),annotation_position='top left',row=2,col=1)
fig.add_vline(x=Gmax, line_width=1.5, line_dash="dash", line_color='#388A73',annotation_text='max:%s'%round(Gmax,1),row=2,col=1)
fig.add_vline(x=Gmean, line_width=1.5, line_dash="dash", line_color='#444614',annotation_text='mean:%s'%round(Gmean,2),annotation_position='bottom right',row=2,col=1)
fig.show()


# In[22]:


get_ipython().system('brew services stop mongodb-community@5.0')

