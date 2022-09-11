#!/usr/bin/env python
# coding: utf-8

# # Best Athlete of Event - Time Complexity

# In[1]:


from myfunc import *
from myclasses import *
from mysimfunc import *
import itertools
from pymongo import MongoClient
import sqlalchemy as sa


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


# ## Time Complexity
# 
# In order to answer the question which athlete places first most often, each possible combination has to be iterated. This leads to the topic of time complexity.
# 
# To assess an algorithms efficiency the Big Oh notation **O()** is commonly used. It describes the growth of an algorithm in a worst case scenario and is independent from the machine or implementation. A lower order of growth shall be favored. For example one for loop with one operation has the notation O(n), because the constant operation will be performed n times and the n is the dominant term.
# 
# Not concidering the creation of athlete objects, the simulation has three for loops with two loops nested in an outer loop.
# This would lead to O(n) for the outer loop and O(n) for each inner loop.
# 
# According to the law of addition sequantial statements are added. For the two inner loops this means $O(n) + O(n) = O(2n)$ because both loops are dominated by n iterations. However for Big Oh notation the constant *2* can be dropped, which gives $O(n)$ for the inner loops *swimrace and award_ceremony*.<br>
# For nested statements the law of multiplication has to be applied. Thus the outer loop gives the total algorithm's time complexy $ O(m) * O(n) = O(m*n) $
# 
# For the outer loop the nation *m* is used, because it is know that the ranges have different length. For ranges of same length the notation would be $O(n^2)$
# 
# ```
# for i in range(10000):
#         award_ceremony(swim_race(race_participants,DictAthleteObjects),DictAthleteObjects,injured)
# ```
# 
# 1)      i in range (10000):
# 2)              swimrace: i in range (8)
# 3)              award_ceremony: i in range (8)
# 
# 
# To simulate all possible combinations an additional outer for-loop has to be added. Therefore *k* is added because it is known that length will be different than 10000.
# 
# $ O(n)*O(m)*O(k) = O(n*m*k) $
# 
# This Big O notation reveals that the algorithm is not linear but also not polynominal or exponential.
# 
# Because we know that swimrace and award_ceremony have the length of 8 and the simulation range is 10000, it is possible to say that those loops have $ 2x8x10000 = 160000 $ constant iterations for $ k $. Therefore the algorithm's behaviour in terms of order of growth is assumed being close to a linear. Thus the range $ k $ for the outer loop leads to unknown iterations over all possible combinations, which is a main issue.
# 
# 
# ## Iterating possible combinations
# 
# Below print statement shows the amount of iterations which are possible. Those are leading to a long runtime when iterating with iteration.combinations(). At this point another approach has to be found to simulate all possible combinations.
# 
# 1) A tournament with several races and qualification phase shall be simulated to get a gold winner instead of first place for every race.<br>This includes another random factor to generate the participants in qualification phases.
# 2) Smarter calculation for equal results. For example, comparing the mean of normal distributions, when those are validly assumed. Or single probabilities on athlete pairs.
# 3) Using multiprocessing modules or other technical approaches for faster calculation (e.g. reducing the time complexity or working with other languages than Python).
# 4) Finding an event type with less athletes to verify that the simulation approach is working on smaller iterables.
# 
# **No 1** is a valid approach with additional randomness in the form of not knowing who is in the qualification group. This would lead to a small redesign of the simulation.
# 
# **No 2** and **No 3** might be valid approachs. Those could be discussed with computer scientist and / or mathematicians in a real business case.
# 
# The single probabilities approach was actually programmed and assessed, but it is not working for 8 athletes racing simultaneously. Instead single probabilites could be calculated to get the probability of winning consecutive races by one by one. I actually seeked guidance on Math StackExchange and the User Greg Martin answered that for simultaneous races not enough information is provided. [Link to my Question on Math StackExchange.](https://math.stackexchange.com/questions/4518903/allowed-to-multiply-probabilities-that-way-single-probabilities-for-a-simulta)
# 
# **No 4** will be applied in the code below. From Data Exploration a few unfavored event types where examind. As result the 200m Backstroke event for male athletes will be used for simulation. It seems to be so unpopular for the Top 100 male athletes that it "only" provides 495 combinations for 12 athletes. Code and Results are in the chapter *Best Athlete of Event - Simulation*.
# 
# 

# In[6]:


myDict = generate_objects(male_athlete_ids,mycol,'100m Freestyle','50m',injured=False)
print('For 100m Freestyle on 50m courses there are %s male athletes.\nFor races between 8 athletes this gives %s possible combinations.'%(len(myDict.keys()),count_combinations_without_replacement(len(myDict.keys()),8)))


# In[7]:


myDict = generate_objects(male_athlete_ids,mycol,'200m Backstroke','50m',injured=False)
print('For 400m Freestyle on 50m courses there are %s male athletes.\nFor races between 8 athletes this gives %s possible combinations.'%(len(myDict.keys()),count_combinations_without_replacement(len(myDict.keys()),8)))


# In[8]:


get_ipython().system('brew services stop mongodb-community@5.0')

