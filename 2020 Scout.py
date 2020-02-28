#This scrip pulls data for prescouting at the 2019 events
import requests
import json
import fnmatch
import pygal
from pygal.style import LightColorizedStyle as LCS, LightenStyle as LS
import numpy as np
from collections import OrderedDict 
from operator import getitem 


#Base TBA api url.  This will be used in all of the API calls
READ_URL_PRE = 'https://www.thebluealliance.com/api/v3/'

#This is the event that you are prescouting it determines the team list to be scouted
event='2020isde2'
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

#print(teams)
#print(number_of_teams)

#print(match_data)


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
    no_line = 0
    for match in match_data:

        if match['actual_time'] != None :
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
                init_pos = match['score_breakdown'][alliance_color]['initLineRobot'+str(position)]
                if init_pos == 'Exited':
                    no_line = no_line + 1
    #Write data out to scout_data datastructure
    scout_data[current_team].update({'no_qual_matches': no_qual_matches})
    scout_data[current_team].update({'end_location': [no_none, no_park, no_hang]})
    scout_data[current_team].update({'initiation_line': no_line})
    
#print(scout_data['frc2342'])

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




blue_cells_inner_auto = []
red_cells_inner_auto = []
blue_cells_outer_auto = []
red_cells_outer_auto = []
blue_cells_bottom_auto = []
red_cells_bottom_auto = []
blue_cells_inner_tele = []
red_cells_inner_tele = []
blue_cells_outer_tele = []
red_cells_outer_tele = []

blue_penalties_committed = []
red_penalties_committed = []
blue_opr =[]
red_opr=[]

blue_team_matrix = []
red_team_matrix = []
for match in match_data:
    if match['actual_time'] != None :
        if match['comp_level'] == 'qm':
            blue_team_list=[match['match_number']]
            red_team_list=[match['match_number']]
            blue_cells_inner_auto.append([match['match_number'], match['score_breakdown']['blue']['autoCellsInner']])
            red_cells_inner_auto.append([match['match_number'], match['score_breakdown']['red']['autoCellsInner']])
            blue_cells_outer_auto.append([match['match_number'], match['score_breakdown']['blue']['autoCellsOuter']])
            red_cells_outer_auto.append([match['match_number'], match['score_breakdown']['red']['autoCellsOuter']])


            blue_cells_inner_tele.append([match['match_number'], match['score_breakdown']['blue']['teleopCellsInner']])
            red_cells_inner_tele.append([match['match_number'], match['score_breakdown']['red']['teleopCellsInner']])
            blue_cells_outer_tele.append([match['match_number'], match['score_breakdown']['blue']['teleopCellsOuter']])
            red_cells_outer_tele.append([match['match_number'], match['score_breakdown']['red']['teleopCellsOuter']])

            blue_penalties_committed.append([match['match_number'], match['score_breakdown']['red']['foulPoints']])
            red_penalties_committed.append([match['match_number'], match['score_breakdown']['blue']['foulPoints']])

            
            blue_opr.append([match['match_number'], match['score_breakdown']['blue']['totalPoints']])
            red_opr.append([match['match_number'], match['score_breakdown']['red']['totalPoints']])


            
            for current_team in teams:
                is_in_match = False
                for i in range(3):
                    if match['alliances']['blue']['team_keys'][i] == current_team:
                        blue_team_list.append(1)
                        red_team_list.append(0)
                        is_in_match = True
                    elif match['alliances']['red']['team_keys'][i] == current_team:
                        blue_team_list.append(0)
                        red_team_list.append(1)
                        is_in_match = True
                if not is_in_match:
                    blue_team_list.append(0)
                    red_team_list.append(0)

            blue_team_matrix.append(blue_team_list)
            red_team_matrix.append(red_team_list)
blue_team_matrix_sorted=sorted(blue_team_matrix, key=lambda x: x[0])
red_team_matrix_sorted=sorted(red_team_matrix, key=lambda x: x[0])
blue_cells_inner_auto_sorted = np.asarray(sorted(blue_cells_inner_auto, key=lambda x: x[0]))
red_cells_inner_auto_sorted = np.asarray(sorted(red_cells_inner_auto, key=lambda x: x[0]))
inner_auto = np.delete(np.vstack((blue_cells_inner_auto_sorted,red_cells_inner_auto_sorted)), 0, 1)
blue_cells_outer_auto_sorted = np.asarray(sorted(blue_cells_outer_auto, key=lambda x: x[0]))
red_cells_outer_auto_sorted = np.asarray(sorted(red_cells_outer_auto, key=lambda x: x[0]))
outer_auto = np.delete(np.vstack((blue_cells_outer_auto_sorted,red_cells_outer_auto_sorted)), 0, 1)


blue_cells_inner_tele_sorted = np.asarray(sorted(blue_cells_inner_tele, key=lambda x: x[0]))
red_cells_inner_tele_sorted = np.asarray(sorted(red_cells_inner_tele, key=lambda x: x[0]))
inner_tele = np.delete(np.vstack((blue_cells_inner_tele_sorted,red_cells_inner_tele_sorted)), 0, 1)

blue_cells_outer_tele_sorted = np.asarray(sorted(blue_cells_outer_tele, key=lambda x: x[0]))
red_cells_outer_tele_sorted = np.asarray(sorted(red_cells_outer_tele, key=lambda x: x[0]))
outer_tele = np.delete(np.vstack((blue_cells_outer_tele_sorted,red_cells_outer_tele_sorted)), 0, 1)

blue_penalties_committed_sorted = np.asarray(sorted(blue_penalties_committed, key=lambda x: x[0]))
red_penalties_committed_sorted = np.asarray(sorted(red_penalties_committed, key=lambda x: x[0]))
penalties_committed = np.delete(np.vstack((blue_penalties_committed_sorted, red_penalties_committed_sorted)), 0, 1)

blue_opr_sorted = np.asarray(sorted(blue_opr, key=lambda x: x[0]))
red_opr_sorted = np.asarray(sorted(red_opr, key=lambda x: x[0]))
opr = np.delete(np.vstack((blue_opr_sorted, red_opr_sorted)), 0, 1)




#print(inner_auto.shape)
#print(blue_team_matrix_sorted)
#print(blue_cells_inner_auto_sorted)
#print(red_cells_inner_auto_sorted)
#print(inner_auto)
blue_team_array = np.asarray(blue_team_matrix_sorted)
red_team_array = np.asarray(red_team_matrix_sorted)
team_array = np.delete(np.vstack((blue_team_array, red_team_array)), 0, 1)
#print(team_array.shape)
#print(blue_team_array)


team1 = np.matmul(team_array.T, team_array)
#print(team1.shape)
#print(team1)
inner_auto1 = np.matmul(team_array.T, inner_auto)
outer_auto1 = np.matmul(team_array.T, outer_auto)
inner_tele1 = np.matmul(team_array.T, inner_tele)
outer_tele1 = np.matmul(team_array.T, outer_tele)
penalties_committed1 = np.matmul(team_array.T, penalties_committed)
opr1 = np.matmul(team_array.T, opr)
#print(inner_auto1)
#print(inner_auto1.shape)
inner_auto_est1 = np.matmul(np.linalg.inv(team1), inner_auto1)
outer_auto_est1 = np.matmul(np.linalg.inv(team1), outer_auto1)
inner_tele_est1 = np.matmul(np.linalg.inv(team1), inner_tele1)
outer_tele_est1 = np.matmul(np.linalg.inv(team1), outer_tele1)
penalties_committed_est1 = np.matmul(np.linalg.inv(team1), penalties_committed1)
opr_est1 = np.matmul(np.linalg.inv(team1), opr1)
#print(inner_auto_est1)
#print(outer_auto_est1)

#print(teams)

i=0
for current_team in teams:
    scout_data[current_team].update({'inner_auto_est': inner_auto_est1[i][0]})
    scout_data[current_team].update({'outer_auto_est': outer_auto_est1[i][0]})
    scout_data[current_team].update({'inner_teleop_est': inner_tele_est1[i][0]})
    scout_data[current_team].update({'outer_teleop_est': outer_tele_est1[i][0]})
    scout_data[current_team].update({'penalties_committed_est': penalties_committed_est1[i][0]})
    scout_data[current_team].update({'opr': opr_est1[i][0]})
    i = i+1

#print(scout_data)

current_teams_by_inner_auto = OrderedDict(sorted(scout_data.items(), 
       key = lambda x: getitem(x[1], 'inner_auto_est'), reverse = True))

current_teams_by_outer_auto = OrderedDict(sorted(scout_data.items(), 
       key = lambda x: getitem(x[1], 'outer_auto_est'), reverse = True))

current_teams_by_inner_tele = OrderedDict(sorted(scout_data.items(), 
       key = lambda x: getitem(x[1], 'inner_teleop_est'), reverse = True))

current_teams_by_outer_tele = OrderedDict(sorted(scout_data.items(), 
       key = lambda x: getitem(x[1], 'outer_teleop_est'), reverse = True))

current_teams_by_penalties = OrderedDict(sorted(scout_data.items(),
        key = lambda x: getitem(x[1], 'penalties_committed_est'), reverse = True))

print('Teams by inner auto')
for key, values in current_teams_by_inner_auto.items():
    print(key, values['inner_auto_est'])

print('Teams by outer auto')
for key, values in current_teams_by_outer_auto.items():
    print(key, values['outer_auto_est'])

print('Teams by inner teleop')
for key, values in current_teams_by_inner_tele.items():
    print(key, values['inner_teleop_est'])

print('Teams by outer teleop')
for key, values in current_teams_by_outer_tele.items():
    print(key, values['outer_teleop_est'])

print('Teams by penalties committed')
for key, values in current_teams_by_penalties.items():
    print(key, values['penalties_committed_est'])



import csv

with open('scout.csv', mode='w', newline='') as scout_file:
    scout_writer = csv.writer(scout_file, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    scout_writer.writerow(['Team', 'OPR', 'Inner Auto Cells', 'Outer Auto Cells', 'Inner Teleop Cells', 'Outer Teleop Cells', 'Initation Line', 'Penalties', 'Hang', 'Park', 'None'])
    
    for team in teams:
        opr_ = scout_data[team]['opr']
        in_auto_cells = scout_data[team]['inner_auto_est']
        out_auto_cells = scout_data[team]['outer_auto_est']
        in_tele_cells = scout_data[team]['inner_teleop_est']
        out_tele_cells = scout_data[team]['outer_teleop_est']
        pen = scout_data[team]['penalties_committed_est']
        hang_ = scout_data[team]['end_location'][2]/scout_data[team]['no_qual_matches']
        park_ = scout_data[team]['end_location'][1]/scout_data[team]['no_qual_matches']
        none_ = scout_data[team]['end_location'][0]/scout_data[team]['no_qual_matches']
        inline_ = scout_data[team]['initiation_line']/scout_data[team]['no_qual_matches']



        scout_writer.writerow([team, opr_, in_auto_cells, out_auto_cells, in_tele_cells, out_tele_cells, inline_, pen, hang_, park_, none_])
    
    
    