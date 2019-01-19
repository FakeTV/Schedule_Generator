#!/usr/bin/env python
# -*- coding: utf-8 -*-   
import pandas as pd #needed to read in csv files
import re as re #needed to conduct certain searches
from random import randrange #needed to generate random searches
import math #math related functions like floor, int, and much more
from plexapi.server import PlexServer #needed to pull from the Plex server
import sys

    


class Show():
    # Class used to store information on the set of shows we have
    # Technicaally, this is only good for TV series
    def __init__(self):
        self.title = ""
        self.duration = ""
        self.category = ""
    def __repr__(self):
        return repr((self.title, self.duration, self.category))
    
    def __len__(self):
        return 1
    
class Episode():
    # This class will store information on what we would like to watch
    # If all else fails, we will watch a general movie
    def __init__(self):
        self.category = ""
        self.duration = ""
    def __repr__(self):
        return((self.category,self.duration))
            







 
def LoginToPlex():
    baseurl = "http://192.168.1.87:32400"
    token = "EyGUecHbYGq9HzwxBAEu"
    
    return PlexServer(baseurl,token)

def CreateShow(video,time_shift=0.25):
    show = Show()
    show.title = video.title
    show.title = show.title.replace("&","&amp;")
    show.category = ''
    
    try:
        show.duration = float(video.duration)
        show.duration = show.duration/(1000*3600)
        show.duration = math.ceil(show.duration/(time_shift))*(time_shift) #shift to fit what we are looking for here
    except TypeError:
        show.duration = 1.0
    
#    if video.duration is "None":
#        show.duration = 1.0
#    else:
#        show.duration = float(video.duration)
#        show.duration = show.duration/(1000*3600)
#        show.duration = math.ceil(show.duration/time_shift)*time_shift #shift to fit what we are looking for here
    return show
        


def GenerateSchedule(start_hour,cutoff_time,time_shift,overlap_max,path_to_shows,path_to_schedule):
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    ###
    ###
    # Creation of classes for use later in the script
    ###
    ###
            
    # Sections necessary for our TV shows on the Plex Server
    sections = ['TV Shows General','TV Shows Oldies']

    
    plex = LoginToPlex()
        
    
    
    
    ##### User defined variables
    #start_hour = 6 #time you would like to start the schedule each day (in hours)
    #cutoff_time = 0.25 #time (in hours) you would like scheduled until nothing is scheduled
    #time_shift = 0.25 #time (in hours) that will be used as the "time-shift" variable in output xml
    #path_to_shows = "." #path to the files containing all shows
    #path_to_schedule = "." #path to bulk schedule used to generate .xml schedule
    
    ###
    ###
    ###
    ###
    # Read in variables and store for future use
    ###
    ###
    ###
    ###
#    path_to_shows = "%s/shows.csv" % path_to_shows
    path_to_schedule_csv = "%s/schedule.csv" % path_to_schedule
#    show_temp = pd.read_csv(path_to_shows,sep=',',header=None)
    schedule_temp = pd.read_csv(path_to_schedule_csv,sep='/',header=None,encoding='ISO-8859-1')
    
#    show_temp2 = []
    schedule_temp2 = []
#    show_list = []
    schedule_list = []
#    for i in range(0,len(show_temp)):
#        show_temp2.append(show_temp.iloc[i])
#        show = Show()
#        show.title = show_temp2[i][0]
#        show.duration = show_temp2[i][1]
#        if pd.isnull(show.duration):
#            show.duration = time_shift
#        else:
#            show.duration = math.ceil(show.duration/time_shift)*time_shift #shift to fit what we are looking for here
#        show.category = show_temp2[i][2]
#        if pd.isnull(show.category):
#            show.category = ['default']
#        else:
#            show.category = show.category.split("/")
#            show.category = [item.strip() for item in show.category] #get rid of extra white space as necessary
#        #show.category = show_temp2[i][2].split("/")
#        show_list.append(show)
        
    for i in range(0,len(schedule_temp)):
        schedule_temp2.append(schedule_temp.iloc[i])
        schedule = Episode()
        schedule.category = schedule_temp2[i][0]
        schedule.duration = schedule_temp2[i][1]
        schedule_list.append(schedule)
        
        
    ###
    ###
    ###
    # For later use, put together a list of ALL tv shows with their duration
    ###
    ###
    ###
    show_list = []
    for location in sections:
        tv = plex.library.section(location)
        for video in tv.all():
            show = CreateShow(video,time_shift)
            show_list.append(show)
    
    # Sort the show_list by duration; will make things easier later
    show_list = sorted(show_list,key=lambda show: show.duration)
 
    
    
    
    ###
    ###
    ###
    ###
    # Perform logical snity checks on data.  Add/subtract time where necessary
    ###
    ###
    ###
    ###
    total_hours = sum(i.duration for i in schedule_list)
    
    # Check if less or more than a full day, and change accordingly
    if total_hours != 22 :
       schedule_list[-1].duration = schedule_list[-1].duration + (22-total_hours)
    if schedule_list[-1].duration < 0:
       raise ValueError("Check times for segments, they are creating times less than zero!")
    
    
    
    
    ###
    ###
    ###
    ###
    # Wrap through all shows, write to file as necessary. Break to next section
    # after last section but still have some time left over
    ###
    ###
    ###
    ###
    path_to_schedule_xml = "%s/pseudo_schedule.xml" % path_to_schedule
    
    # Preamble of the file (beginning)
    file = open(path_to_schedule_xml,"w")
    file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r")
    file.write("<schedule>\r")
    file.write("\t<sundays></sundays>\r")
    file.write("\t<mondays></mondays>\r")
    file.write("\t<tuesdays></tuesdays>\r")
    file.write("\t<wednesdays></wednesdays>\r")
    file.write("\t<thursdays></thursdays>\r")
    file.write("\t<saturdays></saturdays>\r")
    file.write("\t<weekends></weekends>\r")
    file.write("\t<everyday>\r")
    
    # Go to every single segment, and add shows accordingly 
    #
    # This will take a few forms
    # - oldies,sitcoms,... : traditional segments that we see everywhere
    # - <Animaniacs>,<CatDog>,...: Calling out shows BY NAME
    # - movies <xtra="contentRating:G,PG ...">: movies subcategory (with optional xtra calls as necessary)
    #
    # If for some reason there is an error in one of the above categories,
    # the script will run general movies with no xtras
    # NOTE: Movies can never be called by name.  This is a limitation of PseudoChannel
    first_show = 1 #will just set "strict timing" to 1 for the first show
    running_time = start_hour #keeps track of the number of hours you have scheduled for the system
    for i in range(0,len(schedule_list)):
        
        single_item = schedule_list[i]
        
        single_item.category = single_item.category.strip()
        
        
        show_refined = []
        error_flag = 0 #initalize the error flag; used to figure out if there is a problem with current section
        number_repeats = 1 #how many times should you repeat the given show?
        time_expired=False #set for the next segment
        # Check first for an exact show title
        if single_item.category.startswith("<"):
            print("Exact Show being called")
            show_string = re.search("<(.*)>",single_item.category)
#            try:
#                number_repeats = show_string.group(2)
#                print("Repeats set at %s" % number_repeats)
#            except:
#                print("Default repeat of 1 assigned")
            show_string = show_string.group(1)
            
            for location in sections:
                tv = plex.library.section(location)
                for video in tv.search(title=show_string):
                    show = CreateShow(video,time_shift)
                    show_refined.append(show)

            if len(show_refined) != 1:
                print("ERROR: Exact show can not be found; either there is no show OR too many shows. Reverting to movie")
                error_flag = 1
#            else:
#                show_chosen = show_refined[0]
                
            
        # Now check if we have a "random" request for literally anything
        elif single_item.category.startswith("random"):
            print("Random Show being selected")
            show_refined = show_list
            
            show_string = re.search("<(.*)>",single_item.category)
            
            try:
                number_repeats = show_string.group(1)
                print("Repeats set at %s" % number_repeats)
            except:
                print("Default repeat of 1 assigned")
#            if len(show_list) !=1:
#                show_number = randrange(0,len(show_list)-1)
#                show_chosen = show_list[show_number]
#            else:
#                show_chosen = show_list[0] #There is apparently only one show
            
        # Now check if we have a movie being called
        elif single_item.category.startswith("movies"):
            if "<" in single_item.category:
                xtras_string = re.search("<(.*)>",single_item.category)
                xtras_string = xtras_string.group(1)
            
                if xtras_string:
                    print("General movie called, xtras to be used")
                    show_refined = Show()
                    show_refined.title = "movie"
                    show_refined.duration = 2
                    show_refined.category = xtras_string
                else:
                    print("ERROR: Nothing in movie brackets!  Reverting to normal movie")
                    error_flag = 1
            else:
                print("General movie called, no xtras present") 
                show_refined = Show()
                show_refined.title = "movie"
                show_refined.duration = 2
        #Now we will handle the more general items
        else:
            print("General show category called")
            
            show_string = re.search("<(.*)>",single_item.category)
            try:
                number_repeats = show_string.group(1)
                print("Repeats set at %s" % number_repeats)
#                print(single_item.category)
                str_replace = "<"+number_repeats+">"
#                print(number_repeats)
#                print(str_replace)
                single_item.category = single_item.category.replace(str(str_replace),'')
                single_item.category = single_item.category.strip()
#                print(single_item.category)
            except:
                print("Default repeat of 1 assigned")
            
            
            
            for location in sections:
                tv = plex.library.section(location)
            
                for video in tv.search(genre=single_item.category):
                    show = CreateShow(video,time_shift)
                    show_refined.append(show)
                    
#            if show_refined:
#                if len(show_refined) != 1:
#                    show_number = randrange(0,len(show_refined)-1)
#                    show_chosen = show_refined[show_number]  
#                else:
#                    show_chosen = show_refined[0] #Since there is only one show
            if not show_refined:
                print("ERROR: Nothing exists in the given genre. Reverting to general movie.")
                error_flag = 1

        while True:
            show_chosen = []
            # We check the error flag set, and if so set the movies standard
            if error_flag is 1:
                show_chosen = Show()
                show_chosen.title = "movie"
                show_chosen.duration = 2
            elif len(show_refined) == 1:
                try:
                    show_chosen = show_refined[0]
                except AttributeError:
                    show_chosen = show_refined
            else:
                show_number = randrange(0,len(show_refined)-1)
                show_chosen = show_refined[show_number]
                
                
            # Set the number of repeats to be used
            # If this is removed, we will default to reading .csv for this information
            if show_chosen.duration <= 0.25:
                number_repeats = 4
            elif show_chosen.duration <= 0.50:
                number_repeats = 3
            elif show_chosen.duration <= 1.00:
                number_repeats = 2
            else:
                number_repeats = 1
            print("Actual number of Repeats Chosen: %s" % number_repeats)
                
                
            # Begin to consider the timing of the system
            # Check how much time we have left for the system, are we still within the amount??
            # If yes, then do it.  If not, then add the time to the next section and move on
            # if this is the last section, break this for loop altogether and start the "final" loop
            for j in range(0,int(number_repeats)):
                print("Duration of chosen element: %s" % show_chosen.duration)
                print("Time left in given segment: %s" % single_item.duration)
                
                if show_chosen.duration > single_item.duration:
                    print("Time expired!  Checking for next section")  
                    time_expired = True
                    break
                
                # Now we will check a couple things
                # - First show?  If so set strict-timing and set the flag to 0
                # - Check the hour we should be placing, mins as well
                hour = []
                minute = []
                
                if show_chosen.title is "movie":
                    file.write('\t<time title="random" type="movie" ')
                else:
                    print(show_chosen.title.encode('utf8'))
                    file.write('\t<time title="%s" type="series" ' % show_chosen.title.encode('utf8'))
                
                
                if first_show is 1:
                    file.write('strict-time="true" time-shift="%02d" overlap-max="%02d"' %(time_shift*60,overlap_max*60))
                    first_show = 0
                else:
                    file.write('strict-time="false" time-shift="%02d" overlap-max="%02d"' %(time_shift*60,overlap_max*60))
                    
                    
                if show_chosen.title is "movie" and show_chosen.category:
                    file.write(' xtra="%s">' % show_chosen.category)
                else:
                    file.write('>')
                    
                hour = math.floor(running_time % 24)
                minute = (running_time - math.floor(running_time))*60 
                
                file.write('%02d:%02d</time>\r' %(hour,minute))
                
                running_time = running_time + show_chosen.duration
                single_item.duration = single_item.duration - show_chosen.duration
                
            #We check if we ran out of time.  If so, break the while loop
            if time_expired:
                break
            
            
        # If we are not on the last element, move timeup to the next section then move on
        # If this is the last element, then we need to fill in the gaps to the very end
        if i != len(schedule_list)-1:
            print("Going to next section...")
            schedule_list[i+1].duration = schedule_list[i+1].duration + single_item.duration
        else:
            print("All sections complete, filling in last gaps")
            while True:
                show_refined = []
                
                if schedule_list[-1].duration < cutoff_time: # we have hit an end since there is no time left
                    print("FINISHING due to CUTOFF_TIME MET")
                    break
                
                show_refined  = list(filter(lambda show: show.duration < schedule_list[-1].duration,show_list))
                
                if not show_refined: # nothing is short enough
                    print("FINISHING due to NO SHOWS SHORT ENOUGH")
                    break
                
                if len(show_refined) != 1:#we need to pick one at random
                    show_number = randrange(0,len(show_refined)-1)
                    show_chosen = show_refined[show_number]
                else:
                    show_chosen = show_refined[0]
                print("Filling in another show")
                
                
                
                file.write('\t<time title="%s" type="series" ' %(show_chosen.title))
                file.write('strict-time="false" time-shift="%02d" overlap-max="%02d"' %(time_shift*60,overlap_max*60))
                file.write('>')
                
                hour = math.floor(running_time % 24)
                minute = (running_time - math.floor(running_time))*60 
                
                file.write('%02d:%02d</time>\r'%(hour,minute))
                
                running_time = running_time + show_chosen.duration
                schedule_list[-1].duration = schedule_list[-1].duration - show_chosen.duration
    
    
    
    # Closing of the file
    file.write("\t</everyday>\r")
    file.write("\t<weekdays></weekdays>\r")
    file.write("</schedule>")
    
    
    file.close()
    print("Schedule generation COMPLETE")






