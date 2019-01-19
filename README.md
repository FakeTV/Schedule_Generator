# Schedule_Generator
For those of you interested in a less granular approach to creating schedules for each channel, this is for you.

Concept of the project:
In order to create a schedule file to be used with pseudochannel, you have to go through all your shows and individually pick them, then place them into the schedule.  This is a great way to pinpoint exactly what you want with certain channels.  BUT, if all you want is your huge collection of "Drama" shows to just pick up and play for 6 hours on a channel, this is not easy to do.
This is where this set of scripts comes in.  The .csv file will specify certain genres (or movie specific tags) that you would like playing for a set amount of time.  The script will then go into your plex server, pick a random show in that genre, and place it into a schedule file for you.  By running the script once with your customized .csv file, you'll produce a pseudo-schedule.xml file.

How do you actually setup your csv file?
Great question!  Each line of the csv file represents a new set of shows/movies the script will read. Each line has the following format (you can find an example in here too):


GENRE(for TV) OR "movies"(for Movies)     \<EXTRAS\>       /    #HRS


GENRE: Specific genre coming from your plex server (if instead, you're trying to call movies here, just put "movies" without the quotes
EXTRAS:
- If movies, you can specify tags you'd like your movie to have.  This is exactly what you'd put in your .xml file when editing it directly.
- If TV shows, this can be a number that represents how many times a given TV show will repeat before picking a new one (for example, if you put <3> and it found Scrubs, it will play 3 Scrubs episodes before trying to pick a new show
#HRS: The number of hours you'd like the given command to last. NOTE: It is a good idea that each element be at least 1-2 hours, and that the sum of these numbers is somewhere around 22.  Making it any higher can run into overlap issues near the break.

Before you ask, YES, this script is smart enough to know how long a given show is.  So it does take this into account when looking through your shows.  However, it is not perfect.  If the plex server reports that a given show is usually half an hour, but then the next episode set to play is a 2 hour special, this really can't be handled perfectly.  This is one of  the reasons why leaving a buffer at the end of the day is so nice.


Setup Guide:
Actually very simple:
- Make sure that you have pseudochannel installed.
- (There is a chance you will need to make sure the python package "random" is installed on your system)
- Place all files (except for the .csv files) into the channels folder.
- Edit and place .csv file(s) into the folder(s) of the channels you want this to work with
- Ensure the IP address and Token in the Schedule_Functions.py file have been updated to your values (you can find these in the LoginToPlex() routine, and can be edited with any text editor.
- Run the script!

But how do I run the Script?
Another wonderful question!  It usually is just as simple as "./Schedule_Generation.py", but there are some flags you will probably want to consider setting as well to suit your needs


--path_schedule : This is the path to your .csv file.  Considering you should have put this in a subfolder, this should be the GLOBAL reference to that location (NOTE: this is the path to the folder, NOT the path to the actual .csv file)

--start_hour : the time of day you'd like to start counting in your .xml file 

--cutoff_time : When this amount of time (in hours) is leftover in a given element, it will be rolled over into the next category and the next element will be started.

--time_shift : what you'd like to "round" all your elements too.  For example: time_shift of 0.25 that all times used in the logic of the program will be rounded to the quarter hour.  So that 0.65 hour drama will actually be counted as 0.75 hours.  This allows for "nice times" to be reported in the .xml file if you'd like it.

There are some other ones, but they are mostly defunct now.

------------------------------------------------

Ways to make better:
- Add the config file to correctly interact, so you don't have to retype the ip address and token.
