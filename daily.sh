#!/bin/bash
# Script is set to run daily, and will perform the following functions
# - Kill all channels currently running
# - Go into each channel and perform the update, xml, and generate action
# - Run each channel once (since that seems to be necessary to make this work) for one minuite
# - Run "generate-channels-daily-schedules.sh"
#
# NOTE: If you ever decide to add more channels, make sure to update the number here!

# Move to the correct folder for all commands to follow
cd /home/pi/channels

OUTPUT_PREV_CHANNEL_PATH=.

OUTPUT_PREV_CHANNEL_FILE=".prevplaying"

CHANNEL_DIR_INCREMENT_SYMBOL="_"

CHANNEL_DIR_ARR=( $(find . -maxdepth 1 -type d -name '*'"$CHANNEL_DIR_INCREMENT_SYMBOL"'[[:digit:]]*' -printf "%P\n" | sort -t"$CHANNEL_DIR_INCREMENT_SYMBOL" -n) )

FIRST_RUN=false

# If the previous channel txt file doesn't exist already create it (first run?)
if [ ! -e "$OUTPUT_PREV_CHANNEL_PATH/$OUTPUT_PREV_CHANNEL_FILE" ]; then

	#FIRST_RUN_NUM=$((${#CHANNEL_DIR_ARR[@]}))
	echo 1 > "$OUTPUT_PREV_CHANNEL_PATH/$OUTPUT_PREV_CHANNEL_FILE"

	echo "First run: $FIRST_RUN_NUM"

	FIRST_RUN=true

fi
PREV_CHANNEL=$(<$OUTPUT_PREV_CHANNEL_PATH/$OUTPUT_PREV_CHANNEL_FILE)
#######
#######
#######
# KILL ALL CHANNELS CURRENTLY RUNNING, INCLUDING ALL OTHER BOXES
#######
#######
#######
sudo ./stop-all-boxes.sh


#######
#######
#######
# Run a GLOBAL update of all shows.  This was made in an effort to not take as long to update the channels.
#######
#######
#######
sudo python Global_DatabaseUpdate.py


#######
#######
#######
# UPDATE ALL CHANNELS WITH THE CURRENT INFORMATION, AND GENERATE A TEMPORARY SCHEDULE
# This includes a section that will update the .xml file depending on the kind of schedule you want
#######
#######
#######
for(( i=1; i<=${#CHANNEL_DIR_ARR[@]}; i++ ))
do

sudo python Schedule_Generation.py --path_schedule ${CHANNEL_DIR_ARR[i-1]} --start_hour 6 --cutoff_time 0.50 --time_shift 0.25


cd ${CHANNEL_DIR_ARR[i-1]}

sudo python PseudoChannel.py -xml -g -m

cd ..

done


#######
#######
#######
# RUN ALL CHANNELS BECAUSE FOR SOME REASON IT MAKES THINGS WORK BETTER
#######
#######
#######
for(( i=1; i<=${#CHANNEL_DIR_ARR[@]}; i++ ))
do
cd ${CHANNEL_DIR_ARR[i-1]}
sudo ./startstop.sh
sleep 1m
sudo ./startstop.sh
cd ..
done
sudo ./stop-all-channels.sh
sleep 2m

#######
#######
#######
# GENERATE A FINAL DAILY SCHEDULE
#######
#######
#######
#sudo ./generate-channels-daily-schedules.sh



#######
#######
#######
# IF NECESSARY, RESTART A CHANNEL THAT WAS PREVIOUSLY RUNNING
#######
#######
#######
if [ "$FIRST_RUN" = false ]; then

sudo ./manual.sh $PREV_CHANNEL

fi