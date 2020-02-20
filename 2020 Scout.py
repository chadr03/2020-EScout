#This scrip pulls data for prescouting at the 2019 events
import requests
import json
import fnmatch
import pygal
from pygal.style import LightColorizedStyle as LCS, LightenStyle as LS

#Base TBA api url.  This will be used in all of the API calls
READ_URL_PRE = 'https://www.thebluealliance.com/api/v3/'

#This is the event that you are prescouting it determines the team list to be scouted
event='2020week0'
#event='2020txgre'
#This is a list of all events that you will be pulling the prescouting data from
#previous_events=['2019txaus', '2019txelp', '2019txama', '2019txsan', '2019txcha', '2019txpla', '2019txgre', '2019txdel', '2019txpas', '2019txdls', '2019ftcmp']

#sets up some empty lists to be populated later in the program
previous_events_teams=[]
previous_events_matches=[]
event_prescouting_teams=[]
scout_data={}



#sets up the API request session
session = requests.Session()
#sets up the API authorization key --- this is unique for an individual and you can sign on the TBA to get one
session.headers.update({'X-TBA-Auth-Key': 'cRUNcqozsuYyku3CJYaC5rE1QAPvGWrdkknZ4UPPwc3euDq6qg8pxpKpjIhKDLWL'})

#Get team list for all teams in FIT district from TBA API
# url = 'district/2019tx/teams/keys'
# fit_teams = session.get(READ_URL_PRE + url).json()

#Gets team list for the event that is being prescouted from TBA API
url = 'event/' + event + '/teams/keys'

teams = session.get(READ_URL_PRE + url).json()
number_of_teams = len(teams)


url = 'event/' + event + '/matches'

match_data = session.get(READ_URL_PRE + url).json()

print(teams)
print(number_of_teams)

print(match_data)


#with open("file.txt", "w") as output:
#    output.write(str(event_scouting_teams))
#f.write(event_scouting_teams)
#f.close
#https://www.thebluealliance.com/api/v3/event/2020week0/matches
 

""" #Gets team list for each of the previous events in the previous_events list from TBA API
for event in previous_events:
    url = 'event/' + event + '/teams/keys'
    teams = session.get(READ_URL_PRE + url).json()
    previous_events_teams.append(teams)
#create dictionary of {'event': [list of teams]} for each event
previous_events_teams_dict = dict(zip(previous_events, previous_events_teams))
#print(prevoius_events_teams_dict)
"""
"""

#gets match data for each of the previus events in the previous_events list from TBA API
for event in previous_events:
    url = 'event/' + event + '/matches'
    matches = session.get(READ_URL_PRE + url).json()
    previous_events_matches.append(matches)
#create dictionary of {'event': [list of match information]} for each event
previous_events_matches_dict = dict(zip(previous_events, previous_events_matches))
#print(previous_events_matches_dict)
"""

#figure out what previous events teams in current prescouting event participated and place it in dictionry called scout_data {'team_number': {'previous_events': [list of events]}}
for current_team in teams:
    previous_events=[]    
    
    for team in event:
        if current_team == team:
             previous_events.append(event)

    scout_data[current_team] = {'previous_events': previous_events}

#print(scout_data['frc2582'])


#pull out data for each team from prevous matches
for current_team in teams:
    no_qual_matches = 0
    no_park = 0
    no_hang = 0
    no_none = 0
    for match in match_data:
        match_no = match['key']
        
        is_in_match = False #initally assumes current_team not in current match 
        #Sets up a loop to go through all 3 teams in each alliance
        for i in range(3):
            #Determine if current_team was on blue alliance in current match
            #and determine what position
            if match['alliances']['blue']['team_keys'][i] == current_team:
                #print(match_no)
                #print(current_team)
                #print('blue'+str(i+1))
                alliance_color = 'blue'
                position = i+1
                is_in_match = True
            #Determine if current_team is in red alliance on current match
            #and determine what position
            if match['alliances']['red']['team_keys'][i] == current_team:
                #print(match_no)
                #print(current_team)
                #print('red'+str(i+1))
                alliance_color = 'red'
                position = i+1
                is_in_match = True
        #Checks to see if the current_team is in the match and it is a qualification match
        if match['comp_level'] == 'qm' and is_in_match:
            no_qual_matches = no_qual_matches + 1
            #Determines end game position
            endgame_pos = match['score_breakdown'][alliance_color]['endgameRobot'+str(position)]
            if endgame_pos == 'Hang':
                no_hang = no_hang + 1
            if endgame_pos == 'Park':
                no_park = no_park + 1
            if endgame_pos == 'None':
                no_none = no_none + 1
    #Write data out to scout_data datastructure
    scout_data[current_team].update({'no_qual_matches': no_qual_matches})
    scout_data[current_team].update({'end_location': [no_none, no_park, no_hang]})
    
print(scout_data['frc2342'])

#Create Visualizations

chart = pygal.Bar(x_label_rotation=45, show_legend=True, spacing=20, width=1500)
chart.title = 'Normalized End Position'
chart.x_labels = teams

hang=[]
park=[]
none=[]
for team in scout_data:
    hang.append(scout_data[team]['end_location'][2]/scout_data[team]['no_qual_matches'])
    park.append(scout_data[team]['end_location'][1]/scout_data[team]['no_qual_matches'])
    none.append(scout_data[team]['end_location'][0]/scout_data[team]['no_qual_matches'])

chart.add('Hang', hang)
chart.add('Park', park)
chart.add('None', none)
chart.render_to_file('2020Endgame.svg')