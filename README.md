#SDGI

##What is SDGI ?

SDGI (Spike Detection Graphical Interface) is a GUI for data analysis
which find out Action Potential spike in data from Local Field Potential.
Associate to the spike detection, it plot the firing rate per period.

######Version
*current version: [v1.2](/Houet/Japon/archive/master.zip)*

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
Open | Open a file ~~or a stream~~
Configure | Change settings, open configure window
Help | Show this page

*Open a stream is not available yet*

####Button:

Button | Command
-------|--------
Refresh | Apply change and display data plot
Save | Save plot, format: dataname_th={}_tp={}_st={}.png
Quit | Close the application


####Configure window:

Name | Command
-----|---------
Threshold resolution | Change the step between two value
Time period resolution | Change the step between two value
Time resolution | Change the step between two value
Step value | Change the step

*The Step value is used for spike detection, see [here](https://github.com/Houet/Japon#info-about-spike-detection).*

####Main window:

Name | Command
-----|--------
Infos | Show current plotting info
Settings Threshold | Change Threshold value
Setting Time period | Change Time period value
Begin time | Change axis time
End time | Change axis time


##More 

#####Version: what change ?
* addition: you can change step between two comparison
* addition: you can also change the time resolution for a higher precision
* Bug correction: start time = end time now raise a warning
* We delete time begin resolution and time end resolution since they were not usefull

#####Info about spike detection:
Spike are detecting with following algoritm:

*data[t] - data[t + step -1] <  -threshold*

If True, spike is detected, otherwise not.


For more information, please contact. 
