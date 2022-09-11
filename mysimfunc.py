from myclasses import *

'''
This code is not in myfunc.py because the functions below are too unique and of no use for Data Exploration.
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