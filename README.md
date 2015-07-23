#SDGI

##What is SDGI ?

SDGI (Spike Detection Graphical Interface) is a GUI for data analysis
which find out Action Potential spike in data from Local Field Potential.
Associate to the spike detection, it plot the firing rate per period.

######Version
*current version: [v2.1](https://github.com/Houet/Japon/archive/master.zip)*

##How to use it ? 

#####On Window:
1. Download the project.
2. Find interface.exe in SDGI directory and launch it.


#####On Linux:
For linux lovers, just run this in your terminal:

```bash
git clone https://github.com:Houet/japon.git
python3 interface.py
```

######Note:

For linux users, following packages are required:

* [Python3](http://python.org) or more
* [matplotlib](http://matplotlib.org/) with it dependancies:
  * numpy
  * pytz
  * six
  * ...


##Working

####Menu:

Button | Command
-------|---------
Open | Open a file
Help | Show this page


####Button:

Button | Command
-------|--------
Refresh | Apply change and display data plot
Save | Save plot, png format
Quit | Close the application


####Display Options:

Name | Command
-----|--------
Starting time | Change axis time
Ending time | Change axis time
Filter (1, 2) | Show spike on figure
Firing rate | Display firing rate
Moving average | Display moving average
Threshold (up/down) | Display moving average +/- threshold 

####Settings:
For each filter, you can set :

Name | Command
-----|--------
Threshold | Change threshold value
Time period | Change time period for firing rate plot
Method | Change the method to detect spike
Step | Change the step for the "Slope" method

##More 

#####Version: what change ?
* addition: you can now set two filter simultaneously
* addition: you can now choose to display some parameters or just raw data
* addition: you can acces more information by clicking on spike
* Bug correction: trying to plot undefined filter now raise an error


For more information, please contact. 
