#SDGI

## What is SDGI ?

SDGI (Spike Detection Graphical Interface) is a GUI for data analysis
which find out action potential spike in data from local fiels potential.
Associate to the spike detection, it drawn the firing rate per period.

## How to use it ? 

Not surpringly for a GUI, SDGI is simple to use. 
Just find the interface.exe in SDGI directory and launch it.

For linux lovers, just run this in your terminal:

"""
git clone https://github.com:Houet/japon.git
python3 interface.py
"""

####Note:

For linux users, following packages are required: 
Python 3 or more
matplotlib with it dependancies


## Working

Open data file with shorcut "Ctrl + O" or open it by clicking on open.
Then click on refresh.
This programm detect spike by sorting sequence which high changement in a short time:

signal[t] - signal[t-1] < -th

where *th* is the threshold.
Setting Threshold scale allow to adjust your desire.  
Configure allow you to change Threshold resolution, meaning that you can change the step between to value. 
Same for time period resolution. 

You can adjust window time by setting begin time and end time.

SDGI allow you to save your plot.

## More 

For more information, please send an email. 

