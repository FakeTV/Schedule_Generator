#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Schedule creation Script
Purpose: To parse the incoming data for schedule location as well as show legend.
    To then take this information and create a .xml file that will serve as the
    channel generation script for later

Created by: Matthew Tedesco
Created on: 06/07/2018
"""
# TODO: Implement call in shell of this script
# TODO: Consider integration of Python PlexAPI in instead of a Google Sheet
# TODO: cron task to run this element daily so we can update shows and seet a new schedule


### 
###
###
###
# Call the function created above
### 
###
###
###
import Schedule_Functions #Custom made functions by me to use in channel generation
import argparse



parser = argparse.ArgumentParser(description="Channel Generation Script")
parser.add_argument("--showupdate",dest="update_shows",action="store_true",default=False,help="update show elements (Default FALSE) // ONLY KEPT FOR LEGACY SUPPORT")
parser.add_argument("--nogenerate",dest="generate_schedule",action="store_false",default=True,help="DONT Generate the actual schedule (Default TRUE)")
parser.add_argument("--path_shows",dest="path_to_shows",help="Show File Location",default=".")
parser.add_argument("--path_schedule",dest="path_to_schedule",help="Schedule File Location",default=".")
parser.add_argument("--start_hour",dest="start_hour",type=float,default=6,help="Hour (in 24h) when the times will start")
parser.add_argument("--cutoff_time",dest="cutoff_time",type=float,default=0.10,help="Cutoff time (when things stop getting scheduled)")
parser.add_argument("--time_shift",dest="time_shift",type=float,default=0.25,help="amount of time (in hours) to shift the scheduled elements")
parser.add_argument("--overlap_max",dest="overlap_max",type=float,default=0.50,help="variable used to store cutoff-time, the variable that will cancel a show if it runs too late")
parser.add_argument("--debug",dest="debug",action="store_true",default=False,help="run debug script in function (Default FALSE) // ONLY KEPT FOR LEGACY SUPPORT")

args = parser.parse_args()

#Should we update shows?
if args.update_shows:
    Schedule_Functions.UpdateShows(args.document_url,args.path_to_shows)
    
#Should we generate a new schedule?
if args.generate_schedule:
    Schedule_Functions.GenerateSchedule(args.start_hour,args.cutoff_time,args.time_shift,args.overlap_max,args.path_to_shows,args.path_to_schedule)


if args.debug:
    from plexapi.server import PlexServer #needed to pull from the Plex server
#    import sqlite3
#    import datetime
#    import time
    class Show():
        # Class used to store information on the set of shows we have
        # Technicaally, this is only good for TV series
        def __init__(self):
            self.title = ""
            self.duration = ""
            self.category = ""
        def __repr__(self):
            return repr((self.title, self.duration, self.category))
#    
    baseurl = "http://192.168.1.86:32400"
    token = "zrWotz1WMWqxx1VH9XPd"
    
    sections = ['TV Shows General','TV Shows Oldies']
    
    plex = PlexServer(baseurl,token)
#    
#    
    episodes = plex.library.section("TV Shows General").get("Call The Midwife").episodes()
    print(episodes)
    episodes_sum = 0
    for episode in episodes:
        episodes_sum += episode.duration
    episodes_sum = episodes_sum/(len(episodes))
    print(episodes_sum)
    
    print(plex.library.section("TV Shows General").get("Call The Midwife").duration)
#    conn = sqlite3.connect('pseudo-channel_13/pseudo-channel.db')
#    c = conn.cursor()
#    for row in c.execute('SELECT duration FROM shows ORDER BY id'):
#        print row
    
#    for episode in episodes:
#        duration = episode.duration
#        print(duration)
    
    
#    tv_general = plex.library.section('TV Shows General')
##    for video in movies.search(unwatched=True):
##        print(video.title)
##        
##    for video in tv_general.search(unwatched=True):
##        print(video.title)
#    
#    
##    last_episode = tv_general.get('Archer (2009)').episodes()[-1]
##    print(last_episode.duration)
#    
#    show_list = []
#    
#    for location in sections:
#        tv = plex.library.section(location)
#    
##        for video in tv.search(genre='Drama'):
#        for video in tv.search(title='Archer (2009)'):
#            show = Show()
#            show.title = video.title
#            show.category = ''
#            show.duration = float(video.duration)
#            show.duration = show.duration/(1000*3600)
#            show_list.append(show)
#            
#            
#            
#        
#        
#        
##        
##    for client in plex.clients():
##        print(client.title)
#        
#    print('COMPLETE')







#Schedule_Functions.UpdateShows(document_url,save_path)
#GenerateSchedule(6,0.10,0.25, '.', '.')
